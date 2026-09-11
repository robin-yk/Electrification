# Preservation and migration

## September 11 integration

The integration combines origin/main at `59949b8` with the preserved local branch `archive/local-research-20260911` at `ef2e257`. That branch preserves 55 previously local commits and 17 Joule JSON outputs. A merge retains the original commit identities and source references.

The only textual merge conflict was the worker signature in `tools/openmkm_dynamic/run_cjh_feed_ratio_01.py`. The current main signature, including reactor, temperature, flow and pressure-controller options, was retained. The resulting file is identical to the pre-merge main version.

Raw results, generated figures and original log whitespace are retained unchanged. Historical checksums refer to their original generating version, not to the integration commit.

## ScreenJoule migration

ScreenJoule is a separate repository. Its remote main `39de930` contains selected 0D/2D sources and a separate 3D implementation. Nine of the 17 Joule v6 JSON files have exact copies there. The remaining eight and the complete legacy verification pipeline have not been fully migrated.

ScreenJoule also has uncommitted development work. This reorganization does not overwrite, commit or publish those unrelated changes.

The Suite's Joule application remains available until migration and replacement of its build, package, test and figure references are verified. BO's `element_drive.py` and related thermochemistry stay in the Suite. Deleting an application folder alone would break the remaining consumers.

## Retention policy

Keep successful, stopped and superseded runs. A superseded interpretation does not erase its source computation. Link original records from the research guides; do not silently rewrite them into current-model validation.
