provider "google" {
  project = "my-project"
  region  = "us-central1"
}

# CKV_GCP_28: Ensure that Cloud Storage bucket is not anonymously or publicly accessible
resource "google_storage_bucket" "public_bucket" {
  name     = "public-bucket"
  location = "US"
  
  # Insecure: Allows public access
  iam_configuration {
    public_access_prevention = "inherited"  # Not enforced
  }
}

# CKV_GCP_78: Ensure Cloud storage has versioning enabled
resource "google_storage_bucket" "unversioned_bucket" {
  name     = "unversioned-bucket"
  location = "US"
  
  # Missing versioning enabled
}

# CKV_GCP_18: Ensure GKE Control Plane is not public
resource "google_container_cluster" "insecure_cluster" {
  name     = "insecure-cluster"
  location = "us-central1"
  
  # Insecure: Makes control plane public
  private_cluster_config {
    enable_private_endpoint = false
  }
  
  # Insecure: Missing network policies
  # CKV_GCP_12: Ensure Network Policy is enabled on Kubernetes Engine Clusters
  
  # Insecure: Legacy authorization enabled
  # CKV_GCP_7: Ensure Legacy Authorization is set to Disabled on Kubernetes Engine Clusters
  enable_legacy_abac = true
  
  # Insecure: Default service account
  # CKV_GCP_1: Missing Stackdriver Logging
  # CKV_GCP_8: Missing Stackdriver Monitoring
}

# CKV_GCP_11: Ensure that Cloud SQL database Instances are not open to the world
resource "google_sql_database_instance" "insecure_sql" {
  name             = "insecure-sql-instance"
  database_version = "POSTGRES_13"
  region           = "us-central1"
  
  settings {
    tier = "db-f1-micro"
    
    ip_configuration {
      # Insecure: Allow access from anywhere
      authorized_networks {
        name  = "public"
        value = "0.0.0.0/0"
      }
    }
    
    # Missing backup configuration
    # CKV_GCP_14: Ensure all Cloud SQL database instance have backup configuration enabled
  }
} 