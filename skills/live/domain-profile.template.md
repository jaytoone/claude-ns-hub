# omc-live Domain Profile Template
# Copy to .omc/domain-profile.md in your project root and customize.
# Set domain_profile: ".omc/domain-profile.md" in .omc/live-config.json to activate.

## Score Dimensions
# Comma-separated list of dimension names (goal_fidelity is always added automatically)
# Replace with domain-specific axes. Examples below:
#
# ML Research:
#   benchmark_accuracy, ablation_coverage, reproducibility, novelty
#
# Materials Science:
#   dft_error, synthesis_feasibility, novelty, reproducibility
#
# Drug Discovery (pre-clinical):
#   admet_score, binding_affinity, selectivity, synthetic_accessibility
#
# Software Engineering (default):
#   quality, completeness, efficiency, impact
quality, completeness, efficiency, impact

## Score Oracle
# Shell command to run an external evaluator. Use {output_dir} as placeholder.
# stdout must contain key:value lines (one per dimension defined above).
# Set to "none" to use LLM scoring only.
#
# Examples:
#   python eval_benchmark.py --output {output_dir}
#   ./scripts/eval.sh {output_dir} --format keyvalue
#   pytest tests/ --tb=no -q 2>&1 | python scripts/parse_pytest.py
none

## Convergence Rule
# Optional natural-language rule injected into the SCORE PROMPT.
# Describes when the system should consider the task fully converged.
# Leave blank to use default epsilon/plateau_k convergence.
#
# Examples:
#   Converged if benchmark_accuracy > 0.90 AND reproducibility = PASS
#   Converged if all test suites pass and coverage > 80%
#   Converged if admet_score > 0.75 AND binding_affinity < -8.0 kcal/mol
