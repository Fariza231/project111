# Terraform demo design

AWS App Runner provides an HTTPS-managed entrypoint and a non-SSH container runtime. The existing image must be published to public ECR separately. The runtime role can read one existing Secrets Manager secret ARN containing the read key. Plaintext secret contents are not passed to Terraform. Auto-deploy is disabled and the service is deliberately capped to one replica while storage is process-local.

Local checks use Terraform1.13.5 and the locked AWS provider. `terraform test` uses mock_provider "aws"; no actual AWS calls/resources are part of those plan assertions. The examples use a fictional account ID and image path. No Terraform apply or cloud deployment is performed by CI.

Before an authorized real plan/apply: verify account and region; supply a real version-tagged image and secret ARN in the same region; keep state protected and out of Git; review IAM/KMS needs, image immutability and scanning, log/metric retention, cost and the security-review blockers. Managed HTTPS does not fix application authorization or data durability. App Runner instance files/storage are ephemeral, and local docker-run hardening flags are not automatically applied by this service template.

The default local state backend is only sufficient for validation/demo work; configure an encrypted access-controlled remote backend for team deployment. The template intentionally does not create or manage a plaintext secret value.
