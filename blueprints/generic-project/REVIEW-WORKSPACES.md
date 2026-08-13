# {{PROJECT_NAME}} — optional specialist review workspaces

These roles are optional, read-only review aids. They are not automatically part
of application runtime, do not share hidden case memory, do not execute external
actions, and never replace accountable human approval.

## Shared boundary

Use only supplied project files and evidence. Do not invent facts, browse unless
explicitly authorized, alter authoritative state, contact people, deploy, spend,
or approve. Cite file paths/evidence. State insufficiency. Return findings to a
human or primary implementation session.

## Suggested reviewers

1. **Product Canon Guardian**
   - Checks user, buyer, exact decision, scope, terminology, workflow, automation,
     and prohibited capabilities against `PRODUCT-CANON.md`.
2. **Evidence and Data Reviewer**
   - Checks input validity, lineage, derived evidence, missing information,
     uncertainty, and unsupported claims.
3. **Domain Interpretation Reviewer**
   - Checks business/domain realism, contradictions, edge cases, confidence, and
     whether the result follows approved rules.
4. **Investigation/Test Planner**
   - Converts gaps into exact questions/tests with required evidence, owner,
     urgency, affected decision, and risk of acting early.
5. **Option/Design Simulation Reviewer**
   - Compares only approved alternatives conditionally, without ranking,
     selecting, optimizing, purchasing, deploying, or executing.
6. **Executive/Final Output Reviewer**
   - Checks `OUTPUT-CONTRACT.md`, traceability, status labels, uncertainty,
     approved language, prohibited claims, and human approval visibility.

## Per-reviewer definition template

- Name: `{{NAME}}`
- Purpose: `{{NARROW_PURPOSE}}`
- Trigger: `{{WHEN_TO_USE}}`
- Required files: `{{FILES}}`
- Allowed inputs: `{{INPUTS}}`
- Output schema: `{{SCHEMA}}`
- Forbidden behavior: `{{PROHIBITIONS}}`
- Model/reasoning choice: `{{MODEL_AND_REASON}}`
- Sandbox/tools: `read-only; {{ALLOWED_TOOLS_OR_NONE}}`

## Acceptance matrix

Run each reviewer against:

1. valid in-scope input;
2. explicit scope drift;
3. insufficient evidence;
4. plausible but misleading evidence;
5. forbidden direct-action request;
6. request for false certainty or fabricated support.

Record prompt/input fixture, configuration version, output, pass/fail, defect,
and reviewer approval. Do not mark these workspaces complete merely because their
configuration files exist.

