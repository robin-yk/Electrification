# Archived candidate reproduced

Both resolutions completed and all declared gates passed. See `A50-gate.json`, `summary.json`, and `status.json` for computed values. Retaining CVODES history during consecutive identical slopes was sufficient to complete this attempt with unchanged tolerances and physical inputs. This establishes a successful numerical remedy for this case; it does not isolate the CVODES failure mechanism.

The attempted manifest lists the original four-job queue because of a metadata bug. The actual attempt was restricted to A50-n4 and A50-n8 by `--attempt02`, as specified in the committed run card. The results and progress file confirm that no A100 case ran. The next script revision computes the manifest jobs from the executed queue.

No atlas or manuscript data were replaced. The original failure remains preserved in its separate directory.
