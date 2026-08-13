# Release checklist

- [ ] Product boundary and final human-review statement unchanged
- [ ] Ruff, MyPy, Pytest, ESLint, TypeScript, Vitest, production build pass
- [ ] Python and npm dependency audits reviewed; no unresolved critical issue
- [ ] Secret scan clean; production defaults rejected
- [ ] Backup and restore rehearsal passes
- [ ] Alembic upgrade tested on staging copy
- [ ] Environment checklist complete; no default credentials
- [ ] API/frontend smoke test passes behind TLS proxy
- [ ] TimesFM provider/model metadata visible or mock explicitly declared
- [ ] Rollback image tags and database restore point recorded
- [ ] Pilot owner approves final Task 29 gate
