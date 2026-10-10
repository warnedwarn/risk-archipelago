# Survey readiness

| Question | Evidence | Status |
|---|---|---|
| Is the primitive distinct? | Semantic set mutation with three different topology effects | PASS source/tests |
| Does consensus bind all effects? | Relation, matched island, category, and exact severity are compared | PASS source/tests |
| Can duplicates alter the map? | Duplicate path records observation only; replay guard runs before consensus | PASS source/tests/live |
| Is depth deterministic? | `DEEPENS` increments one matched island and takes max severity | PASS source/tests |
| Can a curator publish an empty map? | Curator-only publication requires at least two islands | PASS source/tests |
| Deployment/source match | Finalized StudioNet byte comparison | PASS |
| Live survey | NEW, NEW, DEEPENS, replay rejection, publish, readback | PASS (`ATLAS-1791581902`) |
| Public browser | Canonical Cloudflare map uses reviewed deployment | PASS desktop/mobile (`evidence/browser-verification.json`) |
