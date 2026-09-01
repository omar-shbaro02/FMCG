# Client demo guide

This demo is a deterministic, local showcase of VAI's controlled FMCG
growth-quality workflow. It uses synthetic data and the mock forecast adapter;
it does not require model downloads, cloud accounts, or client information.

## Start and verify

Requirements: Docker Engine with Compose v2, or Podman. From the repository root:

```bash
make demo
```

Open <http://localhost:3000> and sign in with:

- Email: `admin@example.com`
- Password: `development-admin-only`

Before a meeting, confirm the complete demo path:

```bash
make demo-check
```

The check fails unless the API is healthy, all four cases exist, forecast
evidence and decision-intelligence outputs are readable, both pending and
completed review states are represented, and the mandatory human-review
statement remains present.

The first launch builds the production images and may take several minutes while
dependencies download. Later launches reuse local container-image layers.

## Suggested 8-minute walkthrough

1. **Work queue (1 minute).** Show the four synthetic cases and the mixture of
   `Ready for review` and `Completed` states. Explain that cases are scoped to an
   exact SKU, channel, region, and promotion window.
2. **Loading risk (2 minutes).** Select **[DEMO] Channel loading risk**. Open
   **Case evidence**, then **Growth assessment**. Contrast sell-in movement with
   sell-out evidence and emphasize that the classification is a candidate
   interpretation, not a decision.
3. **Investigation and simulation (2 minutes).** Open **Investigation plan** and
   **Decision simulations**. Point out named evidence gaps, human owners, and
   neutral options. The product does not rank or execute an option.
4. **Executive brief (1 minute).** Show the preserved, traceable draft and its
   visible human-review status.
5. **Human control (2 minutes).** Open **Human review** and either validate the
   loading-risk draft or request specific evidence. Return to the queue to show
   the audited status change. Mention that no price, promotion, budget,
   replenishment, or customer action can be triggered here.

Use **[DEMO] Retained growth candidate** to show a completed review. Use the
temporary-uplift and post-promotion-recovery cases when the client wants to
compare how apparently positive promotions can expose different evidence shapes
and verification needs.

To demonstrate ingestion, open **Datasets**, download **Full synthetic
portfolio**, upload that CSV, and run validation. The file contains 214 rows
across all eight scenario families, including an intentionally short series that
shows how forecast ineligibility remains visible rather than being silently
discarded.

## Presenter notes

- Say “forecast evidence” and “candidate interpretation,” not “the model proved.”
- All figures are synthetic and intentionally shaped to exercise the workflow.
- The demo uses the deterministic mock adapter for speed and repeatability. The
  production TimesFM boundary is replaceable but is not required to demonstrate
  governance, evidence interpretation, and human review.
- Review submission changes an attributed workflow status; it does not execute a
  commercial action.

## Lifecycle commands

```bash
make demo        # build, start, seed, and verify
make demo-check  # run the pre-meeting health and content checks
make demo-logs   # follow API and frontend logs
make demo-stop   # stop containers and preserve demo data
make demo-reset  # remove only the isolated demo containers and volumes
```

After `make demo-reset`, run `make demo` to restore the original deterministic
showcase. The demo uses Compose project name `fmcg-client-demo`, so these commands
do not target the normal development project's database or volumes.

## Troubleshooting

- If ports 3000, 8000, or 5432 are already occupied, stop the normal development
  stack before starting the demo.
- If startup fails, run `make demo-logs` and look first at database migrations and
  API health.
- If a live review changed the prepared state, use `make demo-reset && make demo`
  to restore the presentation baseline.
