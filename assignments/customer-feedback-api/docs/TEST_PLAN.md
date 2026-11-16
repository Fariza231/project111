# Test plan

| Layer | Cases and expected results |
|---|---|
| Unit: validation | Required fields, wrong types, nonobject/array/null bodies, whitespace-only text, malformed email, numeric-string/boolean/fractional ratings,1/5 boundaries,0/6 rejection, length limits, Unicode, unknown/prototype keys, no input mutation. |
| Unit: storage | Sequential IDs, defensive copies, absent lookup, per-instance isolation, deliberate restart data loss and capacity bound. |
| HTTP integration | Correct201/Location/exact response;200 list/ID;404 missing ID;400 invalid ID/data/malformed JSON; invalid create does not persist or consume ID;20 concurrent creates yield unique IDs. |
| Security negatives |413 oversized body,429 throttling even with spoofed forwarding headers, production startup failure without a strong key,401 protected GET/HEAD, valid authorized reads, safe500 and logs, Helmet headers and request IDs. |
| Container integration | Real HTTP readiness, valid create, unauthorized list refusal, authenticated list/single lookup,404 missing record and400 invalid create; UID1000, read-only/capability restrictions; graceful SIGTERM exit0. |
| Terraform | fmt/init/validate plus one mock plan scenario containing five assertions: manual image deployment, secret reference, one instance, safe health path and scoped IAM. No real AWS plan/apply. |
| CI | Run the same Node/audit/container/Terraform checks through the committed root Actions workflow. Read actual remote run status when accessible; a workflow definition alone is not proof of success. |

The isolated app factory creates a new memory store and limiter for each test. Supertest drives the real Express middleware/routes; tests do not mock away HTTP validation. Unit storage tests separately prevent state-mutation mistakes. Coverage is an indicator, not proof of correctness: the measured core modules are app.js, feedback.js and validation.js. The server entrypoint is exercised through actual container startup/shutdown, outside the Node test coverage percentages.

Reproduce final checks: `npm ci --ignore-scripts`, `npm run check`, `npm run test:coverage`. Reproduce the selected archived draft defects: `npm run test:initial` (expected failure). Never substitute the archived draft for production imports.
