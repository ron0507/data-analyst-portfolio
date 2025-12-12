#!/usr/bin/env python3
"""
S3 Data Lake Bucket Manager using boto3

This script provides utilities to create and manage S3 buckets for a data lake
architecture with multiple zones (landing, raw, curated, analytics).
"""

import boto3
import json
import logging
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, BotoCoreError


class S3DataLakeManager:
    """Manages S3 buckets and folder structure for a data lake."""
    
    def __init__(self, region: str = 'us-east-1', profile: Optional[str] = None):
        """
        Initialize the S3 Data Lake Manager.
        
        Args:
            region: AWS region to create resources in
            profile: AWS profile name (optional)
        """
        self.region = region
        
        # Initialize boto3 session
        if profile:
            session = boto3.Session(profile_name=profile)
            self.s3_client = session.client('s3', region_name=region)
        else:
            self.s3_client = boto3.client('s3', region_name=region)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_data_lake_bucket(
        self,
        project: str,
        environment: str = 'dev',
        zones: List[str] = None,
        enable_versioning: bool = True,
        enable_encryption: bool = True,
        tags: Dict[str, str] = None
    ) -> Dict[str, str]:
        """
        Create a data lake S3 bucket with proper configuration.
        
        Args:
            project: Project name for bucket naming
            environment: Environment (dev, staging, prod)
            zones: List of data lake zones to create as folders
            enable_versioning: Enable S3 versioning
            enable_encryption: Enable server-side encryption
            tags: Additional tags to apply
            
        Returns:
            Dictionary with bucket information
        """
        if zones is None:
            zones = ['landing', 'raw', 'curated', 'analytics']
        
        if tags is None:
            tags = {}
        
        # Generate bucket name
        bucket_name = self._generate_bucket_name(project, environment)
        
        try:
            # Create the bucket
            self._create_bucket(bucket_name)
            
            # Configure bucket settings
            if enable_versioning:
                self._enable_versioning(bucket_name)
            
            if enable_encryption:
                self._enable_encryption(bucket_name)
            
            # Block public access
            self._block_public_access(bucket_name)
            
            # Create zone folders
            self._create_zone_folders(bucket_name, zones)
            
            # Apply tags
            bucket_tags = {
                'Project': project,
                'Environment': environment,
                'ManagedBy': 'boto3-script',
                'Purpose': 'data-lake',
                **tags
            }
            self._apply_tags(bucket_name, bucket_tags)
            
            # Configure lifecycle rules
            self._configure_lifecycle_rules(bucket_name)
            
            result = {
                'bucket_name': bucket_name,
                'region': self.region,
                'zones': zones,
                'versioning_enabled': enable_versioning,
                'encryption_enabled': enable_encryption
            }
            
            self.logger.info(f"Successfully created data lake bucket: {bucket_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create data lake bucket: {str(e)}")
            raise
    
    def _generate_bucket_name(self, project: str, environment: str) -> str:
        """Generate a unique bucket name."""
        import random
        import string
        
        # Clean project name
        clean_project = ''.join(c.lower() for c in project if c.isalnum() or c == '-')
        clean_environment = ''.join(c.lower() for c in environment if c.isalnum() or c == '-')
        
        # Add random suffix to ensure uniqueness
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        bucket_name = f"{clean_project}-{clean_environment}-data-lake-{suffix}"
        
        # Ensure bucket name is valid (max 63 characters)
        if len(bucket_name) > 63:
            bucket_name = bucket_name[:57] + suffix
        
        return bucket_name
    
    def _create_bucket(self, bucket_name: str) -> None:
        """Create the S3 bucket."""
        try:
            if self.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            self.logger.info(f"Created bucket: {bucket_name}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                raise ValueError(f"Bucket name '{bucket_name}' already exists globally")
            elif error_code == 'BucketAlreadyOwnedByYou':
                self.logger.warning(f"Bucket '{bucket_name}' already exists and is owned by you")
            else:
                raise
    
    def _enable_versioning(self, bucket_name: str) -> None:
        """Enable versioning on the bucket."""
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            self.logger.info(f"Enabled versioning for bucket: {bucket_name}")
        except ClientError as e:
            self.logger.error(f"Failed to enable versioning: {e}")
            raise
    
    def _enable_encryption(self, bucket_name: str) -> None:
        """Enable server-side encryption on the bucket."""
        try:
            encryption_config = {
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
            
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration=encryption_config
            )
            self.logger.info(f"Enabled encryption for bucket: {bucket_name}")
        except ClientError as e:
            self.logger.error(f"Failed to enable encryption: {e}")
            raise
    
    def _block_public_access(self, bucket_name: str) -> None:
        """Block all public access to the bucket."""
        try:
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            self.logger.info(f"Blocked public access for bucket: {bucket_name}")
        except ClientError as e:
            self.logger.error(f"Failed to block public access: {e}")
            raise
    
    def _create_zone_folders(self, bucket_name: str, zones: List[str]) -> None:
        """Create placeholder objects for each data lake zone."""
        try:
            for zone in zones:
                key = f"{zone}/.keep"
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=b'placeholder file for data lake zone',
                    ContentType='text/plain'
                )
                self.logger.info(f"Created zone folder: {zone}/")
        except ClientError as e:
            self.logger.error(f"Failed to create zone folders: {e}")
            raise
    
    def _apply_tags(self, bucket_name: str, tags: Dict[str, str]) -> None:
        """Apply tags to the bucket."""
        try:
            tag_set = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            self.s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={'TagSet': tag_set}
            )
            self.logger.info(f"Applied tags to bucket: {bucket_name}")
        except ClientError as e:
            self.logger.error(f"Failed to apply tags: {e}")
            raise
    
    def _configure_lifecycle_rules(self, bucket_name: str) -> None:
        """Configure lifecycle rules for the bucket."""
        try:
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'expire-temp-files',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'temp/'},
                        'Expiration': {'Days': 7}
                    },
                    {
                        'ID': 'expire-noncurrent-versions',
                        'Status': 'Enabled',
                        'Filter': {},
                        'NoncurrentVersionExpiration': {'NoncurrentDays': 90}
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            self.logger.info(f"Configured lifecycle rules for bucket: {bucket_name}")
        except ClientError as e:
            self.logger.error(f"Failed to configure lifecycle rules: {e}")
            raise
    
    def upload_sample_data(self, bucket_name: str, local_file_path: str, s3_key: str) -> None:
        """
        Upload a sample data file to the data lake.
        
        Args:
            bucket_name: Target S3 bucket name
            local_file_path: Path to local file
            s3_key: S3 object key (path)
        """
        try:
            self.s3_client.upload_file(local_file_path, bucket_name, s3_key)
            self.logger.info(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")
        except ClientError as e:
            self.logger.error(f"Failed to upload file: {e}")
            raise
    
    def list_bucket_contents(self, bucket_name: str, prefix: str = '') -> List[Dict]:
        """
        List contents of a bucket with optional prefix filter.
        
        Args:
            bucket_name: S3 bucket name
            prefix: Optional prefix to filter objects
            
        Returns:
            List of objects in the bucket
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"')
                    })
            
            return objects
            
        except ClientError as e:
            self.logger.error(f"Failed to list bucket contents: {e}")
            raise
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> None:
        """
        Delete a bucket and optionally all its contents.
        
        Args:
            bucket_name: S3 bucket name
            force: If True, delete all objects first
        """
        try:
            if force:
                # Delete all objects first
                objects = self.list_bucket_contents(bucket_name)
                if objects:
                    delete_keys = [{'Key': obj['key']} for obj in objects]
                    self.s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': delete_keys}
                    )
                    self.logger.info(f"Deleted {len(objects)} objects from bucket")
            
            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
            self.logger.info(f"Deleted bucket: {bucket_name}")
            
        except ClientError as e:
            self.logger.error(f"Failed to delete bucket: {e}")
            raise


def main():
    """Example usage of the S3DataLakeManager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create S3 data lake bucket')
    parser.add_argument('--project', required=True, help='Project name')
    parser.add_argument('--environment', default='dev', help='Environment name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--profile', help='AWS profile name')
    
    args = parser.parse_args()
    
    # Create data lake manager
    manager = S3DataLakeManager(region=args.region, profile=args.profile)
    
    # Create the data lake bucket
    result = manager.create_data_lake_bucket(
        project=args.project,
        environment=args.environment,
        tags={
            'Owner': 'data-team',
            'CostCenter': 'analytics'
        }
    )
    
    print(f"\nData Lake Bucket Created Successfully!")
    print(f"Bucket Name: {result['bucket_name']}")
    print(f"Region: {result['region']}")
    print(f"Zones: {', '.join(result['zones'])}")
    print(f"Versioning: {'Enabled' if result['versioning_enabled'] else 'Disabled'}")
    print(f"Encryption: {'Enabled' if result['encryption_enabled'] else 'Disabled'}")


if __name__ == '__main__':
    main()

