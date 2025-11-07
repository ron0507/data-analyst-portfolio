terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "random_string" "bucket_suffix" {
  length  = 6
  upper   = false
  lower   = true
  numeric = true
  special = false
}

locals {
  bucket_name_base = lower(regexreplace("${var.project}-${var.environment}-data-lake", "[^a-z0-9-]", ""))
  bucket_name      = substr("${local.bucket_name_base}-${random_string.bucket_suffix.result}", 0, 63)
  normalized_db    = lower(regexreplace("${var.project}_${var.environment}_lake", "[^a-z0-9_]", "_"))
  common_tags = merge(
    {
      "Project"     = var.project
      "Environment" = var.environment
      "ManagedBy"    = "terraform"
    },
    var.tags
  )
}

resource "aws_s3_bucket" "data_lake" {
  bucket        = local.bucket_name
  force_destroy = var.force_destroy

  tags = merge(local.common_tags, {
    "Name" = "${var.project}-${var.environment}-data-lake"
  })
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "expire-temp-files"
    status = "Enabled"

    filter {
      prefix = "${var.temporary_prefix}/"
    }

    expiration {
      days = var.temporary_retention_days
    }
  }

  dynamic "rule" {
    for_each = var.enable_noncurrent_expiration ? [1] : []

    content {
      id     = "expire-noncurrent"
      status = "Enabled"

      noncurrent_version_expiration {
        noncurrent_days = var.noncurrent_retention_days
      }
    }
  }
}

resource "aws_s3_object" "zone_placeholders" {
  for_each = toset(var.zones)

  bucket  = aws_s3_bucket.data_lake.id
  key     = "${each.value}/.keep"
  content = "placeholder"

  tags = local.common_tags
}

resource "aws_iam_role" "glue" {
  name                 = "${var.project}-${var.environment}-glue-role"
  assume_role_policy   = data.aws_iam_policy_document.glue_trust.json
  force_detach_policies = true

  tags = local.common_tags
}

data "aws_iam_policy_document" "glue_trust" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "glue_data_lake_access" {
  statement {
    sid    = "ListAndReadDataLake"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [aws_s3_bucket.data_lake.arn]
  }

  statement {
    sid    = "ObjectAccess"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:GetObjectVersion",
      "s3:DeleteObjectVersion",
      "s3:ListBucketMultipartUploads",
      "s3:AbortMultipartUpload"
    ]

    resources = ["${aws_s3_bucket.data_lake.arn}/*"]
  }

  statement {
    sid    = "GlueLogging"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_data_lake_access" {
  name   = "${var.project}-${var.environment}-glue-data-lake-access"
  role   = aws_iam_role.glue.id
  policy = data.aws_iam_policy_document.glue_data_lake_access.json
}

data "aws_caller_identity" "current" {}

resource "aws_glue_catalog_database" "this" {
  name = local.normalized_db

  description = "Data lake database for ${var.project} (${var.environment})"

  create_table_default_permission {
    permissions = ["SELECT"]

    principal {
      data_lake_principal_identifier = "IAM_ALLOWED_PRINCIPALS"
    }
  }

  tags = local.common_tags
}

resource "aws_glue_crawler" "raw_zone" {
  name          = "${var.project}-${var.environment}-raw-crawler"
  role          = aws_iam_role.glue.arn
  database_name = aws_glue_catalog_database.this.name
  description   = "Crawler for raw zone of ${var.project} data lake"

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/${var.raw_zone_prefix}/"
  }

  recrawl_policy {
    recrawl_behavior = var.crawler_recrawl_behavior
  }

  lineage_configuration {
    crawler_lineage_settings = "ENABLE"
  }

  configuration = jsonencode({
    Version  = 1.0
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  dynamic "schedule" {
    for_each = length(trimspace(var.crawler_schedule)) > 0 ? [var.crawler_schedule] : []

    content {
      schedule_expression = schedule.value
    }
  }

  tags = local.common_tags
}
