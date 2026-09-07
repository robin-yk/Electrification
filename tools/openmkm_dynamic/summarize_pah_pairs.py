"""Report one paired mechanism batch: the light layer, then the heavy pool.

Two questions, kept apart. First, how far the C0 to C4 layer moves when the
mechanism changes, which is a disagreement between two calculations and says
nothing about which is right. Second, how much carbon the tested mechanism
carries past C6. Which mechanism was tested is read from the batch manifest, so
this reports a CRECK batch and a GRI batch without being told twice.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHORT = {"creck": "CRECK", "gri": "GRI"}
LIGHT = ("CH4", "C2H2", "C2H4", "C2H6", "C3H3", "C4H2", "C6H2", "C6H6", "CO", "H2")
RINGS = ("C10H8", "C12H8", "C14H10", "C16H10")
FEED_LABEL = {"co2": "CH4/CO2", "h2o": "CH4/H2O"}


def carbon_counts(mechanism):
    """Carbon atoms per species, from whichever mechanism the batch named."""
    import cantera as ct
    path = ROOT / mechanism
    return {s: g.n_atoms(s, "C") for g in [ct.Solution(str(path) if path.exists() else mechanism)]
            for s in g.species_names}


def yields(ratios, counts):
    """Carbon per inlet carbon for every species the case reported."""
    return {s: n * counts[s] for s, n in ratios.items() if s in counts}


def heavy_pool(ratios, counts):
    """Carbon per inlet carbon above C6, split into rings, BIN lumps and rest."""
    cy = yields(ratios, counts)
    heavy = {s: v for s, v in cy.items() if counts[s] >= 7}
    named = {r: heavy.get(r, 0.) for r in RINGS}
    bins = sum(v for s, v in heavy.items() if s.startswith("BIN"))
    total = sum(heavy.values())
    return dict(total=total, named_rings=named, BIN=bins,
                other=total - sum(named.values()) - bins,
                top=sorted(((s, v) for s, v in heavy.items()), key=lambda kv: -kv[1])[:6])


def pct(x):
    return f"{100 * x:.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, required=True)
    a = ap.parse_args()
    data = a.archive / "data"
    rows = json.loads((data / "summary.json").read_text())
    status = json.loads((data / "status.json").read_text())
    manifest = json.loads((data / "manifest.json").read_text())
    gates = json.loads((data / "gates.json").read_text())
    assert status["status"] == "completed", "batch did not complete"
    key = manifest.get("mechanism_key", "creck")
    label, short = manifest["mechanism"], SHORT[key]
    counts = carbon_counts(manifest.get(
        "mechanism_file", "tools/cantera/mechanisms/creck2003-ht-soot-nox.yaml"))

    analysis, lines = [], []
    for row in rows:
        creck = row[key]["metrics"]
        aramco = row["aramco"]["metrics"]
        cy_c = yields(creck["mol_per_feed_carbon"], counts)
        cy_a = yields(aramco["mol_per_feed_carbon"], counts)
        pool = heavy_pool(creck["mol_per_feed_carbon"], counts)
        pool_a = heavy_pool(aramco["mol_per_feed_carbon"], counts)
        analysis.append(dict(feed=row["feed"], T_C=row["T_C"], tau_s=row["tau_s"],
                             aramco_archive=row["aramco"]["archive"],
                             light={s: {key: cy_c.get(s, 0.), "aramco": cy_a.get(s, 0.)}
                                    for s in LIGHT},
                             CH4_conversion={key: creck["CH4_conversion"],
                                             "aramco": aramco["CH4_conversion"]},
                             **{"heavy_" + key: pool, "heavy_aramco": pool_a}))

    def block(entry):
        conv = entry["CH4_conversion"]
        out = [f"### {FEED_LABEL[entry['feed']]} at {entry['T_C']:g} C and {entry['tau_s']:g} s", "",
               f"Aramco row read from `{entry['aramco_archive']}`.", "",
               f"| Quantity | Aramco | {short} | difference |", "|---|---|---|---|",
               "| CH4 conversion, % | " + pct(conv["aramco"]) + " | " + pct(conv[key])
               + " | " + pct(conv[key] - conv["aramco"]) + " |"]
        for s in LIGHT:
            v = entry["light"][s]
            if max(v[key], v["aramco"]) < 1e-6:
                continue
            out.append(f"| {s} carbon, % of inlet C | {pct(v['aramco'])} | {pct(v[key])} | "
                       + pct(v[key] - v["aramco"]) + " |")
        h, ha = entry["heavy_" + key], entry["heavy_aramco"]
        out += ["", f"| Above C6, % of inlet C | Aramco | {short} |", "|---|---|---|",
                f"| all species with 7 or more carbons | {pct(ha['total'])} | {pct(h['total'])} |"]
        for r in RINGS:
            out.append(f"| {r} | {pct(ha['named_rings'][r])} | {pct(h['named_rings'][r])} |")
        out += [f"| BIN lumps | {pct(ha['BIN'])} | {pct(h['BIN'])} |",
                f"| remainder above C6 | {pct(ha['other'])} | {pct(h['other'])} |", "",
                f"Largest {short} carriers above C6: "
                + ", ".join(f"{s} {pct(v)} %" for s, v in h["top"] if v > 0) + ".", ""]
        return out

    lines += [f"# Paired mechanism comparison: {label} against the archived Aramco map", "",
              f"Generated by `tools/openmkm_dynamic/summarize_pah_pairs.py` from "
              f"`{a.archive.name}`. Commit `{manifest['commit'][:7]}`, "
              f"{status['conditions']} conditions, {status['gates_passed']} gates, "
              f"{status['wall_s']:.1f} s.", "",
              "Carbon is per total inlet carbon, which is all methane on the steam feed and "
              "half CO2 on the CO2 feed. The two feeds are one scale only after the CO2 "
              "figures are doubled.", "",
              "The two mechanisms are two models. The light-layer differences below are a "
              "disagreement between two calculations and do not say which is closer to a real "
              "reactor. AramcoMech 2.0 has no species above C8 and no ring above benzene, so "
              "its column above C6 is zero by construction and not a prediction of zero. "
              + manifest["limitations"], ""]
    for entry in analysis:
        lines += block(entry)
    lines += ["## Gates", "",
              "| Gate | largest disagreement, carbon fraction |", "|---|---|"]
    lines += [f"| {g['name']} | {g['max_abs_carbon_fraction']:.3g} |" for g in gates]
    lines += ["", "Cold control at 26.85 C returned zero methane conversion to 1e-8. Sampling "
              "gates repeat one condition per feed at 40 phase points instead of 20 and compare "
              "the C7+ fraction, the BIN fraction and every named ring.", "",
              "## What this does not establish", "",
              "The BIN species are lumped soot precursors inside a gas-phase mechanism with no "
              "particle dynamics, so the BIN carbon is a mechanism output and not a predicted "
              "soot yield. Neither mechanism has been compared against measured product data at "
              "these conditions. Four conditions are a sample, not a map.", ""]
    (a.archive / "REPORT.md").write_text("\n".join(lines))
    (a.archive / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    print("wrote", a.archive / "REPORT.md")


if __name__ == "__main__":
    main()
