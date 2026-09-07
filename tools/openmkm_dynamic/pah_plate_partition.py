"""Regroup the two archived mechanism-pair batches into one carbon partition per bar.

The paired batches under docs/research/pah-pairs-2026-09-07 and
docs/research/pah-pairs-gri-2026-09-07 each carry the full outlet composition per
condition. A figure wants six blocks per mechanism, not 497 species, so this
script buckets every species by its carbon number and prints one JSON row per
condition. It computes; it does not run the reactor, and it invalidates nothing.

The two archives must agree on the condition list, and each partition must close
on the inlet carbon, or the script raises.

    python3 tools/openmkm_dynamic/pah_plate_partition.py > partition.json
"""
import json
from pathlib import Path

import cantera as ct

ROOT = Path(__file__).resolve().parents[2]
# The Aramco rows live inside the CRECK archive: that batch read them from the
# constant-temperature maps to compare against, so both mechanisms of a pair are
# in the same summary file.
ARCHIVES = {"creck": "docs/research/pah-pairs-2026-09-07",
            "gri": "docs/research/pah-pairs-gri-2026-09-07"}
MECHANISMS = {"gri": "gri30.yaml",
              "aramco": "tools/cantera/mechanisms/aramco20.yaml",
              "creck": "tools/cantera/mechanisms/creck2003-ht-soot-nox.yaml"}
BLOCKS = ("CH4", "COx", "otherC1toC5", "C2H2", "C6", "aboveC6")
CLOSURE = 5e-3


def carbon_counts(path):
    local = ROOT / path
    return {s: g.n_atoms(s, "C")
            for g in [ct.Solution(str(local) if local.exists() else path)]
            for s in g.species_names}


def partition(mol_per_feed_carbon, counts):
    """Carbon fraction in each block. Species with no carbon contribute nothing."""
    out = dict.fromkeys(BLOCKS, 0.)
    for species, moles in mol_per_feed_carbon.items():
        n = counts.get(species, 0)
        if not n:
            continue
        carbon = moles * n
        if species == "CH4":
            out["CH4"] += carbon
        elif species in ("CO", "CO2"):
            out["COx"] += carbon
        elif species == "C2H2":
            out["C2H2"] += carbon
        elif n >= 7:
            out["aboveC6"] += carbon
        elif n == 6:
            out["C6"] += carbon
        else:
            out["otherC1toC5"] += carbon
    return out


def main():
    counts = {k: carbon_counts(v) for k, v in MECHANISMS.items()}
    summaries = {k: json.loads((ROOT / v / "data/summary.json").read_text())
                 for k, v in ARCHIVES.items()}
    rows = []
    for creck_row, gri_row in zip(summaries["creck"], summaries["gri"]):
        condition = (creck_row["feed"], creck_row["T_C"], creck_row["tau_s"])
        assert condition == (gri_row["feed"], gri_row["T_C"], gri_row["tau_s"]), \
            "the two archives disagree on the condition list"
        row = dict(feed=condition[0], T_C=condition[1], tau_s=condition[2])
        for mech, metrics in (("gri", gri_row["gri"]["metrics"]),
                              ("aramco", creck_row["aramco"]["metrics"]),
                              ("creck", creck_row["creck"]["metrics"])):
            moles = metrics["mol_per_feed_carbon"]
            block = partition(moles, counts[mech])
            total = sum(block.values())
            assert abs(total - 1.) < CLOSURE, f"{mech} {condition}: carbon closes to {total}"
            # Named carriers the blocks hide, for the caption and the tooltip.
            block["C6H6"] = moles.get("C6H6", 0.) * 6
            block["C10H8"] = moles.get("C10H8", 0.) * 10
            block["BIN"] = sum(v * counts[mech][s] for s, v in moles.items()
                               if s.startswith("BIN") and s in counts[mech])
            block["CH4_conversion"] = metrics["CH4_conversion"]
            block["total"] = total
            row[mech] = block
        rows.append(row)
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
