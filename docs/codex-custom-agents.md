# Codex custom review agents

The six Section 24 workspaces are implemented as project-scoped Codex custom
agents under `.codex/agents/`. They are read-only review specialists, not product
runtime infrastructure or autonomous commercial agents.

## Available agents and model choices

| Agent | Model | Reasoning | Why |
| --- | --- | --- | --- |
| `fmcg_product_canon_guardian` | `gpt-5.6-terra` | high | Fast, careful policy and boundary review. |
| `fmcg_forecast_evidence_reviewer` | `gpt-5.6-terra` | high | Efficient structured evidence and data-quality review. |
| `fmcg_growth_quality_interpreter` | `gpt-5.6` | high | Stronger reasoning for ambiguous, contradictory commercial evidence. |
| `fmcg_investigation_planner` | `gpt-5.6-terra` | high | Efficient conversion of evidence gaps into bounded review questions. |
| `fmcg_decision_simulation_reviewer` | `gpt-5.6` | xhigh | Deepest comparison task across seven conditional options and their interactions. |
| `fmcg_executive_output_reviewer` | `gpt-5.6` | high | Strong contract, traceability, language, and leadership-output judgment. |

`gpt-5.6` is the flagship alias. `gpt-5.6-terra` is used where the work is
narrower and primarily read-heavy. All six agents use a read-only sandbox.

## How to invoke them

Ask Codex explicitly, for example:

- “Use `fmcg_product_canon_guardian` to review this feature proposal.”
- “Have `fmcg_forecast_evidence_reviewer` review this forecast evidence.”
- “Use `fmcg_growth_quality_interpreter` on this validated case envelope.”
- “Have `fmcg_investigation_planner` turn these gaps into exact questions.”
- “Use `fmcg_decision_simulation_reviewer` to compare all seven frozen options.”
- “Have `fmcg_executive_output_reviewer` check this draft against the 12-section contract.”

For a controlled full review, ask Codex to run the relevant agents, wait for all
results, and consolidate them without allowing one agent to overwrite another’s
evidence or conclusions.

Codex discovers project-scoped custom agents when a new project session starts.
Restart or reopen the Codex project session after changing these definitions.

