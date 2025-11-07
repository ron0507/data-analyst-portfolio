output "data_lake_bucket_name" {
  description = "Name of the provisioned S3 data lake bucket."
  value       = aws_s3_bucket.data_lake.bucket
}

output "data_lake_bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  value       = aws_s3_bucket.data_lake.arn
}

output "glue_role_arn" {
  description = "IAM role ARN assumed by AWS Glue crawler and jobs."
  value       = aws_iam_role.glue.arn
}

output "glue_database_name" {
  description = "AWS Glue Data Catalog database that stores table metadata for the data lake."
  value       = aws_glue_catalog_database.this.name
}

output "glue_crawler_name" {
  description = "Name of the AWS Glue crawler responsible for the raw zone."
  value       = aws_glue_crawler.raw_zone.name
}

output "data_lake_zones" {
  description = "List of logical data lake zones created as folder prefixes."
  value       = var.zones
}
