variable "project" {
  description = "Human-readable project identifier used to build resource names and tags."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy the data lake resources into."
  type        = string
  default     = "us-east-1"
}

variable "force_destroy" {
  description = "Whether to allow Terraform to delete the S3 bucket even if it contains objects."
  type        = bool
  default     = false
}

variable "zones" {
  description = "Logical data lake zones that will be represented as folder prefixes within the data lake bucket."
  type        = list(string)
  default     = [
    "landing",
    "raw",
    "curated",
    "analytics"
  ]
}

variable "raw_zone_prefix" {
  description = "Folder prefix that represents the raw zone within the data lake bucket."
  type        = string
  default     = "raw"
}

variable "temporary_prefix" {
  description = "Folder prefix holding temporary files that should expire automatically."
  type        = string
  default     = "temp"
}

variable "temporary_retention_days" {
  description = "Number of days to retain temporary files before lifecycle expiration."
  type        = number
  default     = 7
}

variable "enable_noncurrent_expiration" {
  description = "Enable expiration of noncurrent object versions to control storage costs."
  type        = bool
  default     = true
}

variable "noncurrent_retention_days" {
  description = "How long to retain noncurrent object versions when lifecycle noncurrent expiration is enabled."
  type        = number
  default     = 90
}

variable "crawler_schedule" {
  description = "Optional Glue cron expression to schedule the crawler (e.g. cron(0 3 * * ? * )). Leave blank to disable scheduling."
  type        = string
  default     = ""
}

variable "crawler_recrawl_behavior" {
  description = "Specifies how the crawler should handle previously crawled data (CRAWL_EVERYTHING, CRAWL_NEW_FOLDERS_ONLY, CRAWL_EVENT_MODE)."
  type        = string
  default     = "CRAWL_NEW_FOLDERS_ONLY"
}

variable "tags" {
  description = "Additional tags to apply to all managed resources."
  type        = map(string)
  default     = {}
}

