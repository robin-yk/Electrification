# Local composition pilot stopped before reaction integration

The parent process spent 180.48254941601772 s loading the mechanism and checking the inlet balance. The remaining-time assertion failed before the first 400-sample worker was launched. No reacting output was produced. The empty reason string in status.json is the string representation of that assertion; it does not indicate a chemistry or convergence failure.

The 60% CH4 inlet molar and carbon flow check passes, with the composition-dependent mass flow retained in inlet-checks.json. The 180 s budget was exceeded by 0.48255 s because the parent mechanism-loading call was not interruptible by its own subsequent remaining-time check. The full measured runtime is charged in budget.json. No local retry is authorized by this failure review.

Before another run, place mechanism loading under the same subprocess timeout as reaction integration, and avoid loading the full mechanism a second time for the inlet arithmetic. The remote main push was blocked by approval review, so no GitHub workflow was dispatched. Existing equimolar results and ratio postprocessing remain valid and unchanged.
