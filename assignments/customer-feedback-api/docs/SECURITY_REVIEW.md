# Security review and deployment readiness

## Decision

**Ready for a bounded local/demo evaluation; NOT ready for production customer data.** Functional tests, container execution and Terraform configuration checks do not establish production security. No AWS resources have been deployed and no public cloud endpoint is claimed. Specific Copilot assistance remains unverified because its API was blocked; generated artifacts were assisted/reviewed by Codex and need learner review.

## Implemented controls and evidence

- Strict required fields/types; integer ratings1-5; explicit allowlist; trimmed nonempty text; name100/email254/comment2000 limits; 16kb JSON cap. IDs are positive safe integers. Tests include prototype-related unknown fields, malformed JSON and wrong types.
- Production startup fails closed unless a read key of at least24 characters is configured. GET/HEAD feedback require X-API-Key when configured. Constant-time comparison is used for equal-length buffers; secrets are never returned or logged.
- Helmet, hidden Express fingerprint, generated request IDs and generic JSON errors. Logs contain method, route template, status and request ID, not submitted names, emails, comments or API keys.
- Rate limit60 requests/minute per observed client IP and bounded5000-record memory storage. Forwarding headers are not trusted by default. Body overflow413, throttling429 and capacity503 are tested.
- Runtime image is digest-pinned, uses locked production dependencies, ignores lifecycle scripts, excludes host secrets/test files and runs as UID1000. Code is root-owned/readable. Local smoke test used read-only rootfs, tmpfs, cap-drop ALL, no-new-privileges, memory/CPU/PID limits and loopback-only publishing.
- CI uses read-only repository permissions, pinned action commit SHAs, no persisted checkout token, ordinary pull_request rather than pull_request_target, and no cloud credentials/deployment steps.
- Terraform IAM grants only GetSecretValue on the specified secret ARN. Secret contents are not Terraform inputs. Managed App Runner HTTPS, a health endpoint, explicit deployments and a one-instance cap are configured. Mock tests check those controls.
- npm audit output is retained. Its zero known dependency findings at execution time is not proof that the code or operating-system image has no vulnerabilities. An independent OS/image vulnerability scan was not performed.

## Remaining findings

| Severity | Finding / impact | Required action before production |
|---|---|---|
| High | In-memory records disappear on restart; replicas cannot share data; no backup/recovery guarantees. | Use a durable database/storage adapter, migrations, backup/restore tests and data-retention rules. Revisit IDs and error/retry semantics. |
| High | One shared read key is not per-user/tenant authorization; public POST can receive spam or abusive content. | Implement authenticated identity, scoped read permissions and appropriate abuse prevention. Do not expose all customers' email addresses to arbitrary clients. |
| High | In-memory throttling and unverified reverse-proxy attribution are insufficient for public scaling. | Confirm the deployed proxy chain, configure trusted client attribution deliberately, and use shared throttling/API gateway controls. Do not blindly enable trust proxy. |
| Medium | Names, emails and comments have no approved retention/deletion or privacy process. | Obtain organizational privacy review; define collection purpose, access auditing, consent where applicable, deletion and incident handling. |
| Medium | Terraform state/backend and AWS account guardrails are not configured; real image/secret existence and authorization are untested. | Configure protected encrypted remote state and access controls, validate target account/region and review a real plan. A customer-managed KMS key may require a narrowly scoped Decrypt grant. |
| Medium | A versioned ECR tag can still be mutable; image OS CVEs and platform resource limits are not independently scanned/tested. | Enforce image immutability and registry scanning, patch the base digest regularly, review least privilege and load-test. App Runner does not inherit local docker-run hardening flags automatically. |
| Medium | No persistent metrics, alarms, availability/load tests or disaster-recovery exercise. | Add managed logs/metrics, actionable alerts, capacity tests, and an operational response owner. Verify graceful rollouts with durable storage. |
| Process | Copilot could not complete a model request; no learner manual review is claimed. | Re-run the provided prompts in an authorized Copilot environment if required, critically review outputs, and retain genuine evidence. |

## Safe deployment boundary

Terraform was initialized with backend disabled, validated, formatted and tested with mock_provider "aws". Mock plan tests exercise configuration assertions, not a live AWS plan. Neither terraform apply nor an authenticated AWS API deployment was executed. The provided example image URI and secret ARN are explicitly placeholders. The template creates billable AWS services if a user later authorizes and applies a real plan; this project does not do that automatically.
