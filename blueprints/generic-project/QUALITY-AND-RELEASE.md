# {{PROJECT_NAME}} — quality and release gates

## Continuous checks

- [ ] Formatting and linting pass
- [ ] Strict type/static analysis passes
- [ ] Unit, contract, integration, and UI tests pass
- [ ] Production build succeeds from locked dependencies
- [ ] Database migrations upgrade cleanly and show no schema drift
- [ ] Dependency audit has no unaccepted applicable vulnerability
- [ ] Secret scan is clean
- [ ] Documentation links and example commands work

Record exact commands, versions, counts, warnings, and environment in
`TASK-LOG.md`. “Tests passed” without this evidence is insufficient.

## Security and privacy gate

- [ ] Threat model covers assets, actors, trust boundaries, and abuse paths
- [ ] Authentication, authorization, tenancy, and object access tested
- [ ] Inputs bounded and protected against path, injection, parser, and upload risk
- [ ] Outputs escaped and sensitive fields excluded
- [ ] Production secrets/default credentials rejected
- [ ] Rate limiting and abuse controls verified
- [ ] Audit logs are attributable but do not leak secrets/sensitive payloads
- [ ] Retention, deletion, export, and privacy obligations tested
- [ ] Residual risks have owner and acceptance decision

## Reliability and performance gate

- [ ] Representative and maximum supported sizes tested
- [ ] Concurrency and race-prone transitions tested
- [ ] Retry, idempotency, timeout, and partial-failure behavior verified
- [ ] External dependency outage returns truthful structured failure
- [ ] Index/query performance reviewed
- [ ] Health, readiness, logs, metrics, traces, and alerts tested
- [ ] Backup and restore meet stated RPO/RTO
- [ ] Recovery and rollback rehearsed

## End-to-end gate

For every `SCN-*` in `PROJECT-SPEC.md`, verify:

- real entry point and production-like dependencies;
- correct permissions and data isolation;
- expected state transitions and audit events;
- output contract, traceability, uncertainty, and status;
- human review/correction path;
- prohibited behavior remains absent.

## Deployment checklist

- [ ] Immutable frontend/backend/worker artifacts built
- [ ] Artifact digests and source commit recorded
- [ ] Environment variables validated; no development credential remains
- [ ] Migration tested against a staging copy and backup taken
- [ ] TLS, origins, proxy limits, storage, and network policy configured
- [ ] External provider identity/version/provenance recorded
- [ ] Smoke test passes through the real public route
- [ ] Monitoring and on-call ownership active
- [ ] Rollback artifact and restore point recorded
- [ ] Known limitations published

## Final approval packet

Include:

- approved spec/canon versions;
- task completion summary;
- representative end-to-end scenarios;
- test/security/performance results;
- live smoke evidence;
- migration, backup/restore, and rollback evidence;
- open limitations and residual risks;
- operations/support owners;
- explicit go/no-go decision.

Approval record:

- Release: `{{VERSION}}`
- Commit/artifact: `{{IDENTIFIER}}`
- Environment: `{{ENVIRONMENT}}`
- Decision: `GO | NO_GO | CONDITIONAL_GO`
- Approver: `{{NAME}}`
- Date: `{{YYYY-MM-DD}}`
- Conditions/risks accepted: `{{DETAILS}}`

