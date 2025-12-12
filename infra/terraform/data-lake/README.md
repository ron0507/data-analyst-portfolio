# Data Lake on AWS S3 with AWS Glue Catalog

This Terraform configuration provisions a lightweight data lake foundation on AWS consisting of:

- A secure, versioned S3 bucket segmented into logical `landing`, `raw`, `curated`, and `analytics` zones
- Lifecycle management for ephemeral files and noncurrent object versions
- An AWS Glue Data Catalog database ready to house schema metadata
- An AWS Glue crawler scoped to the raw zone for automated table discovery
- An IAM service role granting the crawler and future Glue jobs access to the data lake bucket

The configuration is intentionally opinionated to provide sensible defaults while remaining easy to customise for different environments.

## Prerequisites

- Terraform `>= 1.5`
- AWS credentials with permissions to manage S3, IAM, and AWS Glue resources
- An S3 bucket name prefix (`project` + `environment`) that is unique enough to avoid naming collisions (a random suffix is appended automatically)

## Usage

1. Navigate to the Terraform directory:

   ```bash
   cd infra/terraform/data-lake
   ```

2. Create a `terraform.tfvars` file (or use environment variables) to supply required inputs. Example:

   ```hcl
   project     = "acme-analytics"
   environment = "dev"
   aws_region  = "us-east-1"

   tags = {
     Owner = "data-platform"
     CostCentre = "analytics"
   }
   ```

3. Initialise and review the plan:

   ```bash
   terraform init
   terraform plan
   ```

4. Apply the configuration when you are satisfied with the plan output:

   ```bash
   terraform apply
   ```

   The outputs printed at the end include the data lake bucket name, Glue database name, and crawler name.

5. (Optional) Configure a crawler schedule by providing a cron expression in `crawler_schedule`. For example, to run every day at 1 AM UTC:

   ```hcl
   crawler_schedule = "cron(0 1 * * ? *)"
   ```

## Uploading Data

The bucket is provisioned with placeholder objects for each zone. You can start populating data by uploading files to the appropriate prefixes. For example, to copy a CSV file into the raw zone:

```bash
aws s3 cp data/sample/customers.csv s3://<bucket-name>/raw/
```

After new data lands in the `raw` prefix, trigger the Glue crawler to refresh the Data Catalog:

```bash
aws glue start-crawler --name <crawler-name>
```

Within a few minutes, the discovered tables will appear inside the Glue database output by Terraform. These tables can be queried from services like Athena or used downstream in Glue ETL jobs.

## Customisation Tips

- **Zones**: Adjust the `zones` variable to introduce additional prefixes (e.g. `sandbox`, `trusted`). Placeholders will be created automatically.
- **Lifecycle Policies**: Disable or tune lifecycle management by tweaking `enable_noncurrent_expiration`, `noncurrent_retention_days`, and `temporary_retention_days`.
- **Glue Access**: Extend the IAM role with additional permissions if you plan to run Glue jobs that interact with other services (e.g. AWS KMS, DynamoDB).

## Clean Up

Set `force_destroy = true` if you want Terraform to delete the bucket even when it contains objects. Otherwise, empty the bucket manually before running `terraform destroy`.

Destroy all resources when the environment is no longer needed:

```bash
terraform destroy
```

