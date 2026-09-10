# Porsin scoping attempt

Attempted on 10 September 2026 using committed generator 5d05275. Conditions: CH4/He 10/90, assumed uniform gas temperature 1900 C, assumed pressure 1 atm, parcel reaction times 20 and 40 ms. Coil-to-gas temperature substitution is recorded in the run card.

Result: no reacting trajectory completed. `ct.Solution` initialization remained active beyond the intended 300-second wall limit. The Python alarm handler did not interrupt the native initialization promptly. The process was stopped externally with SIGTERM; exit code 143. No product prediction or reproduction claim can be extracted from this attempt.

The manifest and failure status are retained. The original mechanism and all previous calculations are unchanged. Before retrying, place the entire worker under an external process timeout and resolve the mechanism initialization cost. No automatic follow-on chemistry was launched.
