# Three physical-waveform mechanism pairs

Purpose: test whether the selected GRI C2 predictions and ranking survive an
Aramco comparison. This is a three-condition pilot, not optimization or a claim
that Aramco is experimentally validated. User requested execution on 2026-09-06.

Inputs: committed wide records 6300012, 6000015, 8300048, read by the generator.
Reconstruct the existing element profile with 25 C ambient. Same profile and
phase grid for both mechanisms. Constant pressure at one atmosphere, prescribed
temperature, energy disabled; equal inlet/outlet mass flow reset each segment
to instantaneous reactor mass divided by residence time. This is the existing
numerical closure, not fixed physical inlet flow or coupled energy optimization.

Execution: cold zero-conversion limit, then sequential GRI/Aramco pairs at 200
and 400 base phase points. Existing hot-window refinement remains enabled.
Maximum 100 cycles per case, minimum 20, full-species boundary tolerance 1e-8.
There are at most 12 reacting executions and one cold check. Expected runtime
5 to 20 minutes; hard workflow limit 30 minutes, single-threaded. Stop on a
failed gate and preserve outputs, with no queued continuation to other pairs.

Acceptance: outlet mass partition 1e-6; C/H/O balance including inventory change
within 0.5 percent of inlet; carbon groups close to solver tolerance; periodic
boundary converged. Refined carbon yields differ by no more than max(0.002,
2 percent of refined value); CH4 conversion differs by at most 0.002. These are
pilot screening tolerances, not experimental validation. Mass partition alone
does not validate the physical flow closure.

Outputs: out/three-pairs contains source records and hashes, physical temperature
grids, full solver outputs including all-species carbon audits, environment and
commit manifest, summary and status. Yield denominator is total inlet carbon,
not converted methane. Absent GRI C6 chemistry is a mechanism limitation, not a
physical prediction of no benzene. No soot model is included.

Cache: no reuse of legacy yields or prior timing tests. Upload partial outputs
even on failure. No existing artifacts are invalidated or overwritten. Generator:
python tools/openmkm_dynamic/run_three_pairs.py. Changes are confined to this
card, the isolated generator and execution workflow; solver modules unchanged.
