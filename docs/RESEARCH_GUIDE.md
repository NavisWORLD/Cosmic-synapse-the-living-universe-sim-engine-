# Research & Validation Guide

## Epistemic labels
Use three labels in issues, papers, and demos:
- **IMPLEMENTED:** the behavior can be inspected in source and reproduced.
- **SIMULATED / HEURISTIC:** the behavior is a model or control mapping.
- **HYPOTHESIS:** the behavior predicts something external and needs an experiment.

## Recommended experiments
### Deterministic world reproducibility
Generate the same named world across clean runs. Compare base world parameters before persistent mutations. Expected result: deterministic base parameters match.

### Sensor response
With consent, run controlled quiet/noise/light/motion conditions. Log 12D and 54D values and test whether the intended channels respond monotonically or consistently.

### Ablation of Φ transform
Compare an adaptive task with Φ-derived channels active vs replaced by matched nonlinear baselines. Pre-register the metric before testing.

### Memory/persistence
Export state before/after controlled actions, restart the browser, and test whether documented local world variables persist.

## Claims this repository does not establish by itself
- that 12D/42D/54D correspond to extra physical spacetime dimensions;
- that browser signals diagnose health, emotion, deception, or consciousness;
- that procedural worlds are real-time remote views of planets;
- that Lorenz or Φ transforms prove a cosmological law;
- that a simulation can physically control Earth or the galaxy.

These boundaries make the research stronger: the code can be tested without requiring acceptance of a larger interpretation.
