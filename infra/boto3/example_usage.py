#!/usr/bin/env python3
"""
Example usage of the S3 Data Lake Manager

This script demonstrates how to use the S3DataLakeManager class to create
and manage data lake buckets with boto3.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path to import our module
sys.path.append(str(Path(__file__).parent))

from s3_bucket_manager import S3DataLakeManager


def example_create_data_lake():
    """Example: Create a complete data lake setup."""
    print("=== Creating Data Lake with boto3 ===\n")
    
    # Initialize the manager
    manager = S3DataLakeManager(
        region='us-east-1',  # Change to your preferred region
        profile=None  # Use default AWS credentials, or specify a profile
    )
    
    # Create data lake bucket with custom configuration
    try:
        result = manager.create_data_lake_bucket(
            project='portfolio-analytics',
            environment='dev',
            zones=['landing', 'raw', 'curated', 'analytics', 'sandbox'],
            enable_versioning=True,
            enable_encryption=True,
            tags={
                'Owner': 'ronith-gadiraju',
                'CostCenter': 'data-analytics',
                'Purpose': 'portfolio-demo'
            }
        )
        
        print("✅ Data Lake Created Successfully!")
        print(f"   Bucket Name: {result['bucket_name']}")
        print(f"   Region: {result['region']}")
        print(f"   Zones: {', '.join(result['zones'])}")
        print(f"   Versioning: {'✅' if result['versioning_enabled'] else '❌'}")
        print(f"   Encryption: {'✅' if result['encryption_enabled'] else '❌'}")
        
        return result['bucket_name']
        
    except Exception as e:
        print(f"❌ Failed to create data lake: {e}")
        return None


def example_upload_sample_data(bucket_name: str):
    """Example: Upload sample data to the data lake."""
    print(f"\n=== Uploading Sample Data to {bucket_name} ===\n")
    
    manager = S3DataLakeManager()
    
    # Path to our sample CSV file
    sample_file = Path(__file__).parent.parent.parent / 'data' / 'sample' / 'customers.csv'
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    try:
        # Upload to raw zone
        s3_key = 'raw/customers/customers.csv'
        manager.upload_sample_data(
            bucket_name=bucket_name,
            local_file_path=str(sample_file),
            s3_key=s3_key
        )
        
        print(f"✅ Uploaded sample data to s3://{bucket_name}/{s3_key}")
        
        # Upload to landing zone as well (simulating different stages)
        landing_key = 'landing/incoming/customers.csv'
        manager.upload_sample_data(
            bucket_name=bucket_name,
            local_file_path=str(sample_file),
            s3_key=landing_key
        )
        
        print(f"✅ Uploaded sample data to s3://{bucket_name}/{landing_key}")
        
    except Exception as e:
        print(f"❌ Failed to upload sample data: {e}")


def example_list_bucket_contents(bucket_name: str):
    """Example: List contents of the data lake bucket."""
    print(f"\n=== Listing Contents of {bucket_name} ===\n")
    
    manager = S3DataLakeManager()
    
    try:
        # List all objects
        objects = manager.list_bucket_contents(bucket_name)
        
        if not objects:
            print("📁 Bucket is empty")
            return
        
        print(f"📁 Found {len(objects)} objects:")
        for obj in objects:
            size_mb = obj['size'] / (1024 * 1024) if obj['size'] > 0 else 0
            print(f"   📄 {obj['key']}")
            print(f"      Size: {size_mb:.2f} MB")
            print(f"      Modified: {obj['last_modified']}")
            print()
        
        # List contents by zone
        zones = ['landing', 'raw', 'curated', 'analytics']
        for zone in zones:
            zone_objects = manager.list_bucket_contents(bucket_name, prefix=f"{zone}/")
            print(f"📂 {zone.upper()} zone: {len(zone_objects)} objects")
        
    except Exception as e:
        print(f"❌ Failed to list bucket contents: {e}")


def example_multiple_environments():
    """Example: Create buckets for multiple environments."""
    print("\n=== Creating Multiple Environment Buckets ===\n")
    
    manager = S3DataLakeManager()
    environments = ['dev', 'staging', 'prod']
    created_buckets = []
    
    for env in environments:
        try:
            result = manager.create_data_lake_bucket(
                project='portfolio-analytics',
                environment=env,
                zones=['landing', 'raw', 'curated', 'analytics'],
                tags={
                    'Environment': env,
                    'Owner': 'data-team',
                    'AutoShutdown': 'true' if env == 'dev' else 'false'
                }
            )
            
            created_buckets.append(result['bucket_name'])
            print(f"✅ Created {env} environment: {result['bucket_name']}")
            
        except Exception as e:
            print(f"❌ Failed to create {env} environment: {e}")
    
    return created_buckets


def example_cleanup(bucket_names: list):
    """Example: Clean up created buckets (use with caution!)."""
    print(f"\n=== Cleanup (Deleting {len(bucket_names)} buckets) ===\n")
    
    # Uncomment the following lines if you want to enable cleanup
    # WARNING: This will delete all buckets and their contents!
    
    # manager = S3DataLakeManager()
    # 
    # for bucket_name in bucket_names:
    #     try:
    #         manager.delete_bucket(bucket_name, force=True)
    #         print(f"🗑️  Deleted bucket: {bucket_name}")
    #     except Exception as e:
    #         print(f"❌ Failed to delete {bucket_name}: {e}")
    
    print("⚠️  Cleanup is commented out for safety.")
    print("   Uncomment the cleanup code in example_cleanup() if you want to delete buckets.")


def main():
    """Run all examples."""
    print("🚀 S3 Data Lake Manager - Example Usage\n")
    
    # Check AWS credentials
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"🔐 AWS Identity: {identity.get('Arn', 'Unknown')}")
        print(f"🏢 Account ID: {identity.get('Account', 'Unknown')}\n")
    except Exception as e:
        print(f"❌ AWS credentials not configured properly: {e}")
        print("   Please configure AWS credentials using:")
        print("   - aws configure")
        print("   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("   - IAM roles (if running on EC2)")
        return
    
    # Example 1: Create a single data lake
    bucket_name = example_create_data_lake()
    
    if bucket_name:
        # Example 2: Upload sample data
        example_upload_sample_data(bucket_name)
        
        # Example 3: List bucket contents
        example_list_bucket_contents(bucket_name)
        
        # Example 4: Create multiple environments
        all_buckets = example_multiple_environments()
        all_buckets.append(bucket_name)
        
        # Example 5: Cleanup (commented out for safety)
        example_cleanup(all_buckets)
        
        print(f"\n🎉 Examples completed! Your main bucket: {bucket_name}")
        print(f"   You can now use this bucket for your data lake operations.")
        print(f"   Remember to delete test buckets when you're done to avoid charges.")


if __name__ == '__main__':
    main()

