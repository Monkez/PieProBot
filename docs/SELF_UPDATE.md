# Self-Update

PiePro uses a two-body self-update model:

- Stable body: current running source.
- Candidate body: copied source under `runtime/bodies/candidate-<timestamp>`.

## Required Flow

1. Create update plan.
2. Create candidate copy.
3. Apply patch to candidate.
4. Validate candidate config.
5. Run candidate tests.
6. Start candidate placeholder.
7. Run candidate health check.
8. Promote only after tests and health pass.
9. Roll back or destroy failed candidates.

## API

- `POST /api/self-update/plan`
- `POST /api/self-update/create-candidate`
- `POST /api/self-update/apply`
- `POST /api/self-update/test`
- `POST /api/self-update/start-candidate`
- `POST /api/self-update/healthcheck`
- `POST /api/self-update/promote`
- `POST /api/self-update/rollback`
- `GET /api/self-update/status`
- `GET /api/self-update/history`

## Safety Rules

- Do not mutate stable directly in a self-update flow.
- Do not promote without passing tests and health checks.
- Do not delete the promoted candidate.
- Do not log secrets.
- Keep rollback data until the replacement is verified.

