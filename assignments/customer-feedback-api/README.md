# Customer Feedback API — AI-Assisted Development and Deployment Readiness

A Node.js24 / Express API implementing the supplied Customer Feedback project. The application, tests, Docker image and Terraform configuration have executable evidence. AI assistance was provided by **Codex**; an actual GitHub Copilot CLI attempt failed during API account validation due to the environment network restriction. It is not presented as a successful Copilot session.

## Run locally

```sh
npm ci --ignore-scripts
npm run check
npm run test:coverage
npm start
```

Development defaults to port3000 and unauthenticated reads, matching the basic exercise. In production, NODE_ENV=production requires READ_API_KEY with at least24 characters and protects GET/HEAD feedback. The example .env file is documentation, not loaded automatically; use your process environment or secret manager.

```sh
curl -i http://localhost:3000/feedback -H 'Content-Type: application/json' \
  -d '{"name":"Anita","email":"anita@example.com","rating":5,"comment":"Excellent product"}'
curl http://localhost:3000/feedback
curl http://localhost:3000/feedback/1
```

| Endpoint | Behavior |
|---|---|
| POST /feedback |201 + id/name/email/rating/comment; Location header; invalid fields400 |
| GET /feedback |200 array; production read key required |
| GET /feedback/:id |200 record,404 missing valid ID,400 invalid ID; production read key required |
| GET /health |200 health result; no customer data or key needed |

Other bounded-resource responses:413 oversized body,429 rate limit,503 memory-store capacity. Errors are JSON and do not expose stacks. Unknown fields are rejected. Names/comments must be nonempty strings; email has a basic structural check; ratings must be integers1-5. Strings are trimmed, with limits described in docs/ACCEPTANCE_CRITERIA.md.

## Docker

```sh
docker build -t customer-feedback-api:local .
export READ_API_KEY="$(node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))")"
docker run --rm --init --read-only --cap-drop ALL --security-opt no-new-privileges \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m --memory 256m --pids-limit 64 \
  -p 127.0.0.1:18080:8080 -e READ_API_KEY customer-feedback-api:local
```

The runtime uses node UID1000, root-owned readable code and a pinned Node24 Alpine base digest. Only production dependencies and src are copied. An optional BuildKit secret named proxy_ca supports inspected build networks without embedding that CA; ordinary public CI builds do not need it. After the container starts, run `API_URL=http://127.0.0.1:18080 READ_API_KEY="$READ_API_KEY" node tools/container-smoke.mjs` from a second shell that has the same key. This helper expects a fresh empty container.

## CI

The active workflow for this repository is `/.github/workflows/customer-feedback-api.yml`; it targets this project subdirectory. The portable `.github/workflows/ci.yml` inside this directory is for using the application as its own repository root. Both install locked dependencies, run syntax/tests/coverage and a production npm audit, build/smoke-test the hardened container, and format/validate/mock-test Terraform. Actions are pinned by commit SHA and repository permissions are contents:read. Test fixture keys are clearly non-production values; no real deployment secrets or AWS credentials are needed.

## Terraform

```sh
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra validate
terraform -chdir=infra test
```

Terraform1.7+ is required; verification used1.13.5. The AWS provider is locked in infra/.terraform.lock.hcl. The App Runner template references an **existing** version-tagged public ECR image and Secrets Manager secret ARN; the checked-in tfvars.example is not a working deployment configuration. No cloud resources were created. Before a separately authorized real deployment, review account/region, image/secret availability, remote state, cost and the security findings. Do not scale this memory-store demo beyond one instance.

## Evidence and project tasks

- Task1: docs/ACCEPTANCE_CRITERIA.md and structured prompt in docs/AI_PROMPTS_AND_REVIEW.md.
- Task2: src/app.js, feedback.js, validation.js and server.js.
- Task3: tests/ and evidence/passing-tests.txt; npm audit evidence.
- Task4: actual initial draft, failing output, fixed validator and red-green explanation; actual first container permission error and correction.
- Task5: Dockerfile, .dockerignore, build/smoke/hardening/shutdown evidence.
- Task6: workflow files and any verified remote run evidence.
- Task7: infra/ configuration, lockfile, mock tests and validation output.
- Task8: docs/SECURITY_REVIEW.md and the final report.

`npm run test:initial` intentionally runs selected tests against the archived defective draft and exits nonzero; it is not part of `npm test`. The final normal suite imports only production code.

**Readiness: local/demo verified; production customer-data deployment is NOT approved.** Storage is process-local and resets on restart; the single read key is not tenant-level authorization; distributed throttling, durable storage, privacy/retention and operational review remain necessary. See the security review for the complete distinction between implemented controls and open findings. No human review or successful Copilot usage is fabricated.

## Submission artifacts

Upload `Customer_Feedback_API_Final_Report.pdf` to the assignment (PDF is accepted). The optional `Customer_Feedback_API_Project.zip` contains the source project for inspection and local execution; ZIP is not an accepted submission format for this prompt.

Verified public CI run: https://github.com/Fariza231/project111/actions/runs/43876618275 (successful for source commit f362b0f). See evidence/github-actions-status.json.
