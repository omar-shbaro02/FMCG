# Controlled prompt guide

Runtime classification is deterministic. Optional LLM use is limited to readable
synthesis. Inputs contain only necessary structured facts, IDs rather than names,
explicit units, uncertainty, allowed schema, forbidden action language, and the
human-review requirement. Output must cite allowed evidence keys, validate under
a strict schema, avoid invented metrics/certainty/actions, and pass at most three
attempts. The gateway has no web or action tools and no cross-case memory.
