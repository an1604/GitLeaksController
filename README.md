# Security Leaks Test Files for Checkov

This directory contains deliberately insecure Infrastructure as Code (IaC) files for testing Checkov's scanning capabilities. These files contain common security issues that Checkov is configured to detect.

## Files Included

1. **aws_s3_insecure.tf** - Terraform file with AWS S3 bucket security issues:
   - Public read-write ACLs
   - Missing block public access settings
   - Missing bucket versioning
   - Missing server-side encryption

2. **gcp_resources_insecure.tf** - Terraform file with GCP security issues:
   - Publicly accessible Cloud Storage buckets
   - Missing versioning in Cloud Storage
   - GKE clusters with public control planes
   - Cloud SQL instances open to the world

3. **insecure_deployment.yaml** - Kubernetes deployment with security issues:
   - Use of default namespace
   - Missing liveness/readiness probes
   - Using latest image tag
   - Running as privileged containers
   - Host network/IPC/PID access
   - Dangerous capabilities
   - Default service account usage
   - Secrets in environment variables

4. **Dockerfile** - Dockerfile with security issues:
   - Running as root (no user creation)
   - Update instructions used alone
   - Credentials in environment variables
   - Exposing sensitive ports

5. **cloudformation_template.yaml** - CloudFormation template with security issues:
   - S3 bucket with public access
   - Overly permissive security groups
   - Lambda without concurrency limits
   - Wildcard IAM permissions
   - Insecure NACL configurations

These files can be used to verify that Checkov correctly identifies the security risks in your Infrastructure as Code. 