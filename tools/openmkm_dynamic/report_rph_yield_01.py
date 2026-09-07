"""Record the rejected acquisition proposal without claiming a reaction result."""
import json
from propose_rph_yield_01 import DEST

def main():
    p=json.loads((DEST/'proposal.json').read_text());a=json.loads((DEST/'acquisition-audit.json').read_text())
    lines=['# Acetylene yield optimization: recommendation rejected','',
        'The single objective is C2H2 carbon yield as percent of total inlet CH4+CO2 carbon. The 39 validated conditions are reused with unchanged input bounds.',
        '',f"The frozen recommendation was {p['peak_C']:g} C, hold {p['hold_s']:g} s and {p['flow_sccm']:g} sccm. Predicted yield was {p['predicted_carbon_yield_pct'][0]:.6g}%, not an Aramco result.",
        '', '| Acquisition diagnostic | Standardized expected improvement |','|---|---|',
        f"| Chosen point | {a['chosen_EI_standardized']:.9g} |",f"| Existing incumbent | {a['incumbent_EI_standardized']:.9g} |",f"| Best of 2048 deterministic Sobol checks | {a['sobol_best_EI_standardized']:.9g} |",
        '', 'The selected point scores below readily available alternatives under the same frozen model and acquisition function. The initial explanation based only on uncertainty was insufficient. Acquisition maximization has failed this quality check; no reaction calculation was dispatched.',
        '',f"The verified incumbent remains {p['incumbent']['y'][0]:.8g}% at 1800 C, 0.5 s hold and 50 sccm. There are still 39 validated 450 C observations.",
        '', 'Preserve this attempt. Before a reviewed retry, improve acquisition initialization/search and require its score to equal or exceed the incumbent and a deterministic reference search. Do not alter chemical gates or report the audit grid point as an optimized or chemically evaluated condition.']
    (DEST/'REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
