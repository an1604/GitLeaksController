provider "aws" {
  region = "us-west-2"
}

# CKV_AWS_57: Ensure ACL does not allow public write permissions
# CKV_AWS_355: Ensure S3 bucket has block public ACLs enabled
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-insecure-bucket"
  acl    = "public-read-write"  # Insecure: allows public write access
}

# Insecure: missing block public access settings
resource "aws_s3_bucket" "insecure_bucket_2" {
  bucket = "another-insecure-bucket"
}

# Missing bucket versioning
resource "aws_s3_bucket" "unversioned_bucket" {
  bucket = "unversioned-bucket"
  
  # Missing versioning configuration
}

# Insecure: Server-side encryption not enabled
resource "aws_s3_bucket" "unencrypted_bucket" {
  bucket = "unencrypted-bucket"
  # Missing server-side encryption configuration
} 