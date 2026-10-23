# GradeLens specification — Phase 11 baseline

## 5.5.4 Written-answer evaluation contract
Written grading is an untrusted draft. The server requests strict JSON with `score`, `justification`, `strengths`, `lackings`, and `suggestions`; validates types and the question mark range; retries once; and flags invalid output for manual grading. Only a teacher can approve and release a result.


## 5.2 Classes
Teachers create unique six-character alphanumeric join codes. Students join once; unknown and duplicate codes are explicit errors. Queries are user-scoped and teacher student lists require ownership.

## Security and release policy

Phase 11 also requires defensive startup logging, request correlation IDs, secure response headers, exact CORS configuration in production, and no secrets in repository files.
JWTs require access scope and support proxy-safe token transports. Role and ownership checks apply at router/service boundaries. Students never receive `ai_*`, teacher drafts, or unreleased scores. Reports are available only for released submissions. Submission deadlines and the single-submission rule are enforced server-side.

## AI grading
Groq is optional and server-only. Written evaluation requests JSON with score, justification, strengths, lackings, and suggestions; responses are fence-stripped, range/list validated, retried once, and invalid responses are flagged for manual grading. MCQs are deterministic. No AI value overwrites teacher fields.

## Deployment verification
Run `alembic upgrade head`, `pytest -q`, and a manual teacher/student journey. Use strong secrets, HTTPS, restricted CORS, external rate limiting, backups, and private object storage in production. Demo credentials are development-only.
