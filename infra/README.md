# Ownership Scanner development infrastructure

This directory defines the Ownership Scanner development environment, deployed
on August 6, 2026:

```text
API Gateway HTTP API
  -> Lambda (Python 3.12, x86_64)
  -> FastAPI through Mangum
  -> packaged, verified canonical CSV dataset
  -> CloudWatch Logs and alarms
```

The public development endpoint is
<https://83fwv16l3j.execute-api.us-east-1.amazonaws.com>. Interactive API
documentation is available at
<https://83fwv16l3j.execute-api.us-east-1.amazonaws.com/docs>, and the OpenAPI
schema is at
<https://83fwv16l3j.execute-api.us-east-1.amazonaws.com/openapi.json>.
This remains a development deployment, not a production service.

## Deployed resources

The bootstrap root defines:

- one private, versioned, encrypted S3 state bucket
- S3 public-access blocking and bucket-owner-enforced ownership
- a bucket policy denying non-TLS requests

The development root defines:

- one dedicated Lambda execution role and one inline logging policy
- one Lambda function with reserved concurrency of five
- one API Gateway HTTP API, default integration route, and default stage
- one Lambda invocation permission restricted to that API
- two 14-day CloudWatch log groups
- four CloudWatch metric alarms
- one $5 monthly AWS cost budget with two email notifications

Terraform also manages remote development state. API throttling is five requests
per second with a burst of ten, both log groups retain data for 14 days, and the
complete application test suite has 45 passing tests. The packaged canonical
dataset contains 13 products.

There is no DynamoDB, WAF, VPC, custom domain, authentication, provisioned
concurrency, Lambda Function URL, X-Ray, dashboard, database, or application-data
S3 access. Those services would add cost and operational complexity without
benefiting the current read-only 13-product development API.

## Likely development cost

API Gateway requests, Lambda invocations and duration, CloudWatch log ingestion
and storage, CloudWatch alarms, S3 state storage, and AWS Budgets may incur cost.
At low development traffic the request, compute, log, and state-storage costs
should be small, but they are not guaranteed to be zero. Four CloudWatch alarms
are expected to be the most consistent recurring resource category. The $5
monthly budget monitors cost; it does not cap or stop spending.

## Prerequisites

- Terraform `>= 1.10.0, < 2.0.0`
- AWS CLI configured through an approved local profile, SSO session, or
  environment-based credential process
- permissions to manage the resources declared by the selected root
- the verified Lambda artifact at `dist/ownership-scanner-lambda.zip`

Never store AWS credentials, account IDs, backend secrets, or personal email
addresses in tracked files. Confirm the intended AWS identity before any plan:

```bash
aws sts get-caller-identity
aws configure get region
```

Review the returned account and principal locally. Do not paste them into Git.

## 1. Build and verify the Lambda artifact

From the repository root:

```bash
python scripts/build_lambda_artifact.py
python scripts/verify_lambda_artifact.py
```

Terraform fails with a clear precondition if the ZIP is absent. The artifact is
gitignored and is not Terraform state.

## 2. Bootstrap the state bucket

The bootstrap root intentionally starts with local Terraform state:

```bash
cp infra/bootstrap/terraform.tfvars.example infra/bootstrap/terraform.tfvars
terraform -chdir=infra/bootstrap init
terraform -chdir=infra/bootstrap fmt -check
terraform -chdir=infra/bootstrap validate
terraform -chdir=infra/bootstrap plan -out=bootstrap.tfplan
```

Set `state_bucket_name` to a globally unique name before planning. Review every
planned action, especially the account, Region, bucket name, encryption,
versioning, public-access block, TLS policy, and `prevent_destroy` lifecycle.

The bootstrap was deployed after review. For any future bootstrap change, apply
only a newly reviewed saved plan with explicit authorization:

```bash
terraform -chdir=infra/bootstrap apply bootstrap.tfplan
```

Bootstrap state remains local initially. The ignored files
`infra/bootstrap/terraform.tfstate*` contain sensitive infrastructure metadata.
Protect them with encrypted local storage and secure backups, restrict filesystem
access, and do not delete them while the bucket is managed by that state. A later
review should decide whether to migrate bootstrap state to a separate protected
backend.

## 3. Configure the development backend

Backend blocks cannot use normal Terraform variables. Create the gitignored file
`infra/environments/dev/backend.hcl`:

```hcl
bucket = "replace-with-the-bootstrap-output"
region = "us-east-1"
```

The tracked backend declares encryption, S3 native lockfiles, and the
environment-specific key `ownership-scanner/dev/terraform.tfstate`. No DynamoDB
lock table is used.

Initialize with the partial backend configuration:

```bash
terraform -chdir=infra/environments/dev init -backend-config=backend.hcl
```

Terraform may copy backend configuration into `.terraform/` and plan files, so
both are ignored and must be handled as sensitive local artifacts.

## 4. Validate and plan development

Optionally copy the example variables file and keep the real file untracked:

```bash
cp infra/environments/dev/terraform.tfvars.example infra/environments/dev/terraform.tfvars
terraform fmt -check -recursive infra
terraform -chdir=infra/environments/dev validate
terraform -chdir=infra/environments/dev plan -out=dev.tfplan
```

Budget creation defaults to disabled in the example configuration. The deployed
development variables enable a $5 monthly budget. Provide the notification email
only in the ignored real `terraform.tfvars` or through a `TF_VAR_` environment
variable. The email variable is marked sensitive. AWS Budgets permissions may
need to be granted separately to the identity running Terraform.

Before any deployment, manually review:

- the AWS identity and Region
- the remote backend and lockfile location
- the Lambda artifact hash, runtime, architecture, handler, memory, timeout, and
  reserved concurrency
- the Lambda role and its two allowed CloudWatch Logs actions
- the API's public default route, payload format, logging, and throttling
- the absence of CORS, authentication, VPC, Function URL, and broad IAM grants
- all alarms and optional budget recipients
- every resource create, update, replace, and delete action

After explicit deployment approval, apply only the saved plan that was reviewed:

```bash
terraform -chdir=infra/environments/dev apply dev.tfplan
```

## Deploying application or dataset updates

CSV changes are packaged into the Lambda ZIP, so rebuild and verify the artifact,
run validation and tests, then create and review a fresh saved plan:

```bash
python scripts/validate_data.py --profile development
python scripts/validate_data.py --profile full
python -m pytest
python scripts/build_lambda_artifact.py
python scripts/verify_lambda_artifact.py
terraform -chdir=infra/environments/dev validate
terraform -chdir=infra/environments/dev plan -out=dev.tfplan
terraform -chdir=infra/environments/dev show -no-color dev.tfplan
```

Do not apply an update until that exact saved plan has been reviewed and
explicitly approved.

## Provider lock files

Run `terraform init` with the reviewed Terraform CLI to generate
`.terraform.lock.hcl` independently in each root. Lock files should be reviewed
and committed; they are intentionally not ignored.

## Rollback and destruction

For an application regression, rebuild a known-good Git revision of the Lambda
artifact, review a new plan, and apply that artifact revision. Terraform does not
retain prior ignored ZIPs automatically.

`terraform destroy` is destructive and requires separate approval plus a saved
state backup and plan review. Destroy the development root before considering
bootstrap cleanup. The state bucket has `prevent_destroy = true`, versioning,
and `force_destroy = false`; removing it requires an intentional code change and
separate handling of retained state versions. Never delete the bucket or local
bootstrap state manually as a shortcut.
