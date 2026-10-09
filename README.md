# Risk Archipelago

## Survey premise

A risk register usually grows by accumulation. Rephrased warnings crowd out genuinely new mechanisms, while the most important cluster may look no different from a single stray note. This project treats the register as changing terrain instead.

Each atlas begins with a bounded scope and a small vocabulary. A surveyor contributes one concrete field note. GenLayer validators compare that complete note with every island already on the map and agree on four state-driving values: relation, matched island, category, and integer severity.

## Three outcomes, three map effects

- `NEW` raises one island whose anchor remains the submitted observation.
- `DEEPENS` adds a contour to exactly one existing island and preserves the highest observed severity.
- `DUPLICATE` records the sounding but leaves the topology untouched.

The contract, not the model, performs those mutations. Island identifiers are derived from observation identifiers, depth increments by one, and publication requires at least two distinct islands. Normalized note fingerprints prevent a fresh wallet from replaying the same wording before consensus.

## Reading the coast

The public application is an atlas rather than a dashboard. The map occupies the working surface. A single field sheet sits below it, and finalized state appears as land, depth contours, or an unchanged echo. Nothing in the composition mirrors the paired control-room project.

## Reproduce the survey

```text
python -m pytest -q
genvm-lint contracts/contract.py
python scripts/deploy.py
python scripts/smoke.py
python scripts/verify_deployment.py
```

The live evidence uses operator-written field notes and operator-controlled wallets. Wallet separation demonstrates replay behavior, not independent institutional authority. Deployment and map receipts are recorded in `deployment.json` and `evidence/` after verification.
