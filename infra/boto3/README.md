# S3 Data Lake Management with boto3

This directory contains Python scripts for creating and managing S3 buckets for a data lake architecture using boto3.

## Files

- **`s3_bucket_manager.py`** - Main class for managing S3 data lake buckets
- **`example_usage.py`** - Comprehensive examples showing how to use the manager
- **`requirements.txt`** - Python dependencies
- **`README.md`** - This documentation

## Features

The `S3DataLakeManager` class provides:

- ✅ **Automated bucket creation** with unique naming
- ✅ **Multi-zone architecture** (landing, raw, curated, analytics)
- ✅ **Security by default** (encryption, versioning, public access blocked)
- ✅ **Lifecycle management** (automatic cleanup of temp files and old versions)
- ✅ **Comprehensive tagging** for cost tracking and organization
- ✅ **Sample data upload** utilities
- ✅ **Bucket content listing** and management
- ✅ **Multi-environment support** (dev, staging, prod)

## Quick Start

### 1. Install Dependencies

```bash
cd infra/boto3
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Make sure you have AWS credentials configured:

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: IAM roles (if running on EC2/Lambda)
```

### 3. Create Your First Data Lake

```bash
# Using the command line interface
python s3_bucket_manager.py --project "my-analytics" --environment "dev"

# Or run the comprehensive examples
python example_usage.py
```

## Usage Examples

### Basic Usage

```python
from s3_bucket_manager import S3DataLakeManager

# Initialize manager
manager = S3DataLakeManager(region='us-east-1')

# Create data lake bucket
result = manager.create_data_lake_bucket(
    project='my-project',
    environment='dev',
    zones=['landing', 'raw', 'curated', 'analytics'],
    tags={'Owner': 'data-team'}
)

print(f"Created bucket: {result['bucket_name']}")
```

### Upload Sample Data

```python
# Upload a CSV file to the raw zone
manager.upload_sample_data(
    bucket_name='my-project-dev-data-lake-abc123',
    local_file_path='data/customers.csv',
    s3_key='raw/customers/customers.csv'
)
```

### List Bucket Contents

```python
# List all objects in the bucket
objects = manager.list_bucket_contents('my-bucket-name')

# List objects in a specific zone
raw_objects = manager.list_bucket_contents('my-bucket-name', prefix='raw/')
```

### Multiple Environments

```python
environments = ['dev', 'staging', 'prod']

for env in environments:
    result = manager.create_data_lake_bucket(
        project='my-project',
        environment=env,
        tags={'Environment': env}
    )
    print(f"{env}: {result['bucket_name']}")
```

## Data Lake Architecture

The created buckets follow a standard data lake architecture:

```
my-project-dev-data-lake-abc123/
├── landing/          # Raw ingested data
│   └── .keep
├── raw/             # Cleaned and validated data
│   └── .keep
├── curated/         # Processed and enriched data
│   └── .keep
├── analytics/       # Analytics-ready datasets
│   └── .keep
└── temp/           # Temporary files (auto-deleted after 7 days)
```

## Security Features

All buckets are created with security best practices:

- 🔒 **Public access blocked** by default
- 🔐 **Server-side encryption** enabled (AES256)
- 📝 **Versioning enabled** for data protection
- 🏷️ **Comprehensive tagging** for governance
- ⏰ **Lifecycle policies** for cost optimization

## Configuration Options

### Zones

Customize the data lake zones:

```python
custom_zones = ['bronze', 'silver', 'gold', 'sandbox']
manager.create_data_lake_bucket(
    project='my-project',
    zones=custom_zones
)
```

### Lifecycle Rules

The default lifecycle configuration:

- **Temporary files** (`temp/` prefix): Deleted after 7 days
- **Noncurrent versions**: Deleted after 90 days
- **Multipart uploads**: Aborted after 7 days

### Tagging Strategy

Default tags applied to all buckets:

```python
{
    'Project': 'your-project-name',
    'Environment': 'dev|staging|prod',
    'ManagedBy': 'boto3-script',
    'Purpose': 'data-lake'
}
```

## Integration with Terraform

This boto3 solution complements the Terraform infrastructure in `../terraform/data-lake/`. You can:

1. **Use Terraform** for production infrastructure (recommended)
2. **Use boto3** for development, testing, or programmatic bucket creation
3. **Combine both** - Terraform for core infrastructure, boto3 for dynamic bucket creation

## Error Handling

The scripts include comprehensive error handling for common scenarios:

- ❌ **Bucket name conflicts** (globally unique names required)
- ❌ **Permission errors** (insufficient AWS permissions)
- ❌ **Region constraints** (bucket creation rules)
- ❌ **Network issues** (retry logic built into boto3)

## Cost Optimization

Built-in cost optimization features:

- 🗑️ **Automatic cleanup** of temporary files
- 📦 **Lifecycle transitions** to cheaper storage classes
- 🏷️ **Detailed tagging** for cost allocation
- 📊 **Version management** to prevent storage bloat

## Troubleshooting

### Common Issues

1. **"Bucket name already exists"**
   - S3 bucket names are globally unique
   - The script adds random suffixes to avoid conflicts
   - Try a more unique project name

2. **"Access Denied"**
   - Check AWS credentials configuration
   - Ensure IAM user/role has S3 permissions
   - Required permissions: `s3:CreateBucket`, `s3:PutObject`, `s3:PutBucketPolicy`, etc.

3. **"Invalid bucket name"**
   - Bucket names must be DNS-compliant
   - Only lowercase letters, numbers, and hyphens
   - Must be 3-63 characters long

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = S3DataLakeManager()
# Now all operations will show detailed logs
```

## Next Steps

After creating your data lake buckets:

1. **Set up AWS Glue** crawlers to catalog your data
2. **Configure Amazon Athena** for querying
3. **Implement ETL pipelines** using AWS Glue or Apache Spark
4. **Set up monitoring** with CloudWatch and CloudTrail
5. **Establish data governance** policies and access controls

## Contributing

To extend the functionality:

1. Add new methods to `S3DataLakeManager` class
2. Update the examples in `example_usage.py`
3. Add corresponding tests
4. Update this documentation

## License

This code is part of the data analyst portfolio project and is available for educational and demonstration purposes.

