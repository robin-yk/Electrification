# Verified quickstart execution

The user requested an executable entry route with the measured runtime workaround, preconditioning, numerical gates, caching, and compact reporting. Run the same CH4/He parcel at 1900 C first as a regression against the committed tight result, then the pending 1800 C check. Load the full mechanism once. Retain feed 10% CH4/90% He, assumed pressure 1 atm, prescribed gas temperature, initial volume 1e-6 m3, and outputs at 20 and 40 ms. No electrical/CFP model.

Apply TZ=UTC0 and LC_ALL=C only to the worker environment with single-thread limits. Compare every species mole fraction to the 1900 C reference within 1e-6 and compare standard/tight species within 1e-6; keep existing mass, atom, temperature, pressure, carbon and metric gates. Abort the next temperature on a failed gate. The full two-temperature worker has a 600-second external cap.

Use `cantera_quickstart.py --check-env` first. The default execution runs two temperatures in one process. Repeating the same command must return a hash-checked cache hit without loading Cantera. Test supervisor timeout with a sleeping dummy child. Preserve old failures and successful results; output uses a content key plus attempt number. Commit the generator and this card before scientific execution. No bulk study, software upgrade or remote dispatch.
