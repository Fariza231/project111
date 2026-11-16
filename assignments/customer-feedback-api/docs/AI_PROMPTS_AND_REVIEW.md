# AI assistance, prompts and review

## Actual tool provenance

Implementation, tests, debugging and configuration were assisted by **OpenAI Codex in this conversation**. GitHub Copilot CLI 1.0.112 was installed and invoked with a testing prompt, but its attempt failed during account validation because the environment cannot access the Copilot endpoint at api.github.com. No Copilot-generated code, test plan or deployment artifact is claimed. See evidence/copilot-attempt.txt. Tasks explicitly naming Copilot therefore still require the learner to reproduce/review the supplied prompts in an authorized Copilot environment if the rubric requires that specific tool.

## Structured development prompt

Role: implement a small Node.js 24 + Express Customer Feedback API. Inputs: required name, email, numeric rating and comment. Endpoints: POST /feedback ->201 with sequential ID and submitted fields; GET /feedback ->200 array; GET /feedback/:id ->200 or404. Reject missing/blank fields, invalid email and invalid rating with400. Use separate app, validation and storage modules; app construction must not listen on a port. State assumptions for ID syntax, integer ratings, length bounds and ephemeral storage. Return generic JSON errors; do not log customer feedback or credentials. Provide unit/integration/negative/boundary tests and instructions to run them. Then provide a non-root Docker image, least-privilege GitHub Actions workflow and basic Terraform infrastructure. Do not apply cloud resources or invent successful tool results.

## Review prompts used as development guidance

1. Requirements: turn the source brief into testable acceptance criteria; distinguish explicit requirements from assumptions.
2. Tests: cover happy paths, each missing field, whitespace, wrong types, rating1/5 boundaries, duplicate/concurrent creates, invalid/missing IDs, malformed/oversized JSON, persistence boundaries, auth and throttling; assert stored state, not status codes alone.
3. Debug: compare initial failing assertions to the validator; explain why truthiness, includes('@') and coercive range checks are insufficient; fix the root causes while retaining the response contract.
4. Container: pin the Node base digest, install locked production dependencies without lifecycle scripts, exclude host secrets and tests, keep source root-owned/readable, run as node, add health and shutdown behavior.
5. CI: run syntax/tests/audit/build/smoke and Terraform checks on push/PR; pin actions by SHA, use contents:read and persist-credentials:false; never deploy infrastructure from an untrusted PR.
6. Infrastructure/security: use an existing public ECR image and Secrets Manager ARN, restrict IAM to that ARN, avoid SSH, rely on managed HTTPS and cap the demo to one replica. Identify why in-memory storage still blocks production readiness.

These prompts are reusable instructions, not fabricated transcripts of Copilot responses. Review was performed by Codex; the learner must inspect the result rather than claiming their own manual review has already happened.

## Actual red-green debugging evidence

The first validator draft used truthiness for strings, includes('@') for email and coercive rating comparisons. Seven tests were executed against that draft; six failed. The original code is retained as docs/initial-validation.js and the original output as evidence/initial-failing-tests.txt. Production validation was then rewritten to check types, trimmed nonempty strings, a structural email pattern and integer boundaries. The final suite is executed against production imports. `npm run test:initial` deliberately reproduces selected initial-draft failures; it is excluded from the normal passing suite.

A second real defect was found by the first container run: owner-only host file permissions made package.json unreadable to UID1000. The image now normalizes /app permissions with root ownership retained. Evidence: docker-initial-startup-error.txt and the successful rebuilt image and smoke checks.

## Learner review before submission

- Read the acceptance criteria and confirm the additional assumptions fit the intended use.
- Inspect validation, authentication, sanitized errors, ID parsing and storage limits.
- Re-run tests and review the actual failures/fixes rather than accepting coverage as proof of correctness.
- If required, run the listed prompts in Copilot and retain the real outputs; the blocked attempt is not evidence of successful Copilot assistance.
- Confirm the report correctly says no AWS deployment was performed and production readiness remains blocked.
