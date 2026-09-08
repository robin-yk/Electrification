# Non-equimolar composition support

## Authorized cloud retry

After the local mechanism-loading timeout, the user approved a GitHub Actions retry on 8 September 2026. The same four conditions and 300-second simulation cap apply. Use `--cloud` and the separate `composition-support-cloud-2026-09-08` output directory; preserve the original failure. The workflow has a 10-minute job limit including setup/upload and a 6-minute simulation-step guard around the internal 5-minute cap. No automatic retries. Download and commit accepted data after review.

User authorization: 8 September 2026, "ㅇㅇ 보강해", following the identified missing non-equimolar waveform coverage. Four support conditions, not a bulk campaign or BO-selected points. One local sequential batch, at most 300 elapsed seconds, single-thread environment. No automatic retries; stop at first failed gate. The previous budget is not reset or charged by this separate bounded pilot.

| CH4 mole fraction | Peak gas temperature, °C | Hot hold, s |
|---|---:|---:|
| 0.7 | 1600 | 0.8 |
| 0.7 | 1800 | 0.5 |
| 0.8 | 1600 | 0.8 |
| 0.8 | 1800 | 0.5 |

Compare with existing 1800 °C, 0.8 s data at each feed fraction. These tests separate a temperature reduction from a hold-time reduction; they do not establish a joint optimum.

Closure: existing AramcoMech 2.0 prescribed-temperature CSTR; undiluted CH4/CO2; 50 sccm at 273.15 K and 101325 Pa; existing 9.228077898393764e-9 m3 fixed volume; 1 atm pressure target. Floor 450 °C; rise 0.025 s; fall 0.10 s; period 1 s. Existing adaptive preconditioner, rtol 1e-11. No energy or transport-model changes.

Execution: one inert waveform check, then paired 400/800 samples per segment at each condition. Worker enforces mass and element integral residual below 1e-3, pressure error below 1e-4, temperature error below 1e-4 K, unchanged volume, and two stable cycles below 1e-7 for both composition output and end state. Pairwise maximum species mol/feed-carbon discrepancy must be below 1e-4. At most 90 s per child and 300 s aggregate, including failed work.

Storage: input and code/mechanism hashes in manifest.json; raw n400/n800 and diagnostics in numbered subfolders; gates.json and status.json preserve acceptance and actual elapsed time. Refuse overwrite or automatic retries. New conditions have no exact cache matches in the audited inventory. Existing feed bracket results remain unchanged.

Generator: tools/openmkm_dynamic/run_composition_support.py. Commit generator and run card before execution. No main manuscript scientific conclusion changes until results are reviewed; inventory and internal progress records are invalidated by accepted new results. Citable results must be committed, not left only in temporary logs.
