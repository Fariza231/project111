# Requirements and acceptance criteria

The source brief specifies Node.js + Express; POST /feedback, GET /feedback and GET /feedback/:id; required name/email/rating/comment; invalid data -> 400, successful create -> 201, successful reads -> 200, missing record -> 404; tests, Docker, CI, Terraform and security review.

| ID | Acceptance criterion | Verification |
|---|---|---|
| AC01 | Valid POST returns 201 and exactly id/name/email/rating/comment; Location points to the new resource. | Supertest integration and container smoke |
| AC02 | GET collection returns 200 with a JSON array, initially empty. | Integration |
| AC03 | GET existing positive ID returns its record; absent valid ID -> 404. | Integration and container smoke |
| AC04 | Missing required fields, blank names/comments, malformed email and rating outside 1-5 -> 400 without saving. | Validation + integration |
| AC05 | Ratings are JSON integers, never coerced numeric strings, booleans or fractions. | Unit boundaries; explicit interpretation of rating requirement |
| AC06 | Name <=100, email <=254, comment <=2000 characters; body <=16kb; schema rejects additional fields. | Unit + integration; resource-hardening assumptions |
| AC07 | Surrounding whitespace is trimmed; Unicode text is preserved. | Unit + integration |
| AC08 | IDs are sequential positive safe integers per process; store is bounded to 5000 records by default. Data is explicitly ephemeral. | Store + concurrent integration tests |
| AC09 | Malformed JSON/IDs ->400, oversized bodies ->413, rate limit ->429, capacity exhaustion ->503; no error stack or request body is returned/logged. | Negative integration tests |
| AC10 | Production cannot start without a >=24-character read key; GET/HEAD feedback require that key, POST remains public. | Integration + live container smoke |
| AC11 | Container runs as node UID1000, supports health checks and graceful shutdown, and can run read-only with all capabilities dropped. | Docker inspection, smoke and shutdown logs |
| AC12 | CI installs from lockfile, executes tests/audit, builds and smoke-tests Docker, and validates/mock-tests Terraform. | Root workflow and actual run evidence when available |
| AC13 | Terraform references an existing image and secret ARN, uses least-privilege IAM, HTTPS-managed App Runner and one instance for memory storage. | terraform fmt/init/validate/test; no apply |
| AC14 | Security review distinguishes demo readiness from unmet production requirements. | SECURITY_REVIEW.md and report |

Assumptions added where the brief is silent: in-memory storage for this small demo; safe-integer IDs; integer star ratings; basic structural email validation (not mailbox verification); trimmed strings; bounded payloads/fields/storage; invalid ID syntax ->400 and missing valid ID ->404. These are explicit choices, not unstated business requirements. Production read protection is additive hardening; the default development-mode endpoints retain the requested unauthenticated example behavior.
