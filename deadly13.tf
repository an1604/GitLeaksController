# GCP Provider configuration
provider "google" {
  project = "example-project"
  region  = "us-central1"
  zone    = "us-central1-a"
}

# AWS Provider
provider "aws" {
  region = "us-west-2"
}

# Insecure GKE Cluster - will trigger multiple GCP checks
resource "google_container_cluster" "insecure_cluster" {
  name               = "insecure-gke-cluster"
  location           = "us-central1"
  initial_node_count = 1

  # Triggers CKV_GCP_1 - Stackdriver logging disabled
  logging_service = "none"

  # Triggers CKV_GCP_8 - Stackdriver monitoring disabled
  monitoring_service = "none"

  # Triggers CKV_GCP_7 - Legacy authorization enabled
  enable_legacy_abac = true

  # Triggers CKV_GCP_18 - Control plane is public
  private_cluster_config {
    enable_private_endpoint = false
    enable_private_nodes    = false
  }

  # Triggers CKV_GCP_12 - Network policy disabled
  network_policy {
    enabled = false
  }

  # Triggers CKV_GCP_65 - No RBAC with Google Groups
  # No configuration for authenticator_groups_config

  # Triggers CKV_GCP_24 - Pod security policy disabled
  pod_security_policy_config {
    enabled = false
  }

  # Missing release channel configuration (CKV_GCP_70)

  # Using default service account (CKV2_GCP_1)
  node_config {
    # Triggers CKV_GCP_22 - Not using Container-Optimized OS
    image_type = "UBUNTU"

    # No workload identity configuration (CKV_GCP_69)
  }

  # Triggers CKV_GCP_25 - Not a private cluster
  # Triggers CKV_GCP_64 - No private nodes

  master_authorized_networks_config {
    # Triggers CKV_GCP_20 - Allows access from anywhere
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "all"
    }
  }
}

# Insecure GCS bucket - will trigger storage checks
resource "google_storage_bucket" "insecure_bucket" {
  name     = "insecure-storage-bucket"
  location = "US"

  # Triggers CKV_GCP_28 - Publicly accessible
  iam_members = [{
    role   = "roles/storage.objectViewer"
    member = "allUsers"
  }]

  # Triggers CKV_GCP_78 - Versioning disabled
  versioning {
    enabled = false
  }

  # Triggers CKV_GCP_29 - No uniform bucket-level access
  uniform_bucket_level_access = false

  # Triggers CKV_GCP_114 - No public access prevention
  # Missing public_access_prevention setting
}

# Insecure Cloud SQL instance - PostgreSQL
resource "google_sql_database_instance" "insecure_postgres" {
  name             = "insecure-postgres-instance"
  database_version = "POSTGRES_13"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    # Triggers CKV_GCP_60 - Public IP enabled
    ip_configuration {
      ipv4_enabled = true
      # Triggers CKV_GCP_11 - Open to the world
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "log_checkpoints"
      value = "off" # Triggers CKV_GCP_51
    }

    database_flags {
      name  = "log_connections"
      value = "off" # Triggers CKV_GCP_52
    }

    database_flags {
      name  = "log_disconnections"
      value = "off" # Triggers CKV_GCP_53
    }

    database_flags {
      name  = "log_lock_waits"
      value = "off" # Triggers CKV_GCP_54
    }

    # Missing backup configuration (CKV_GCP_14)
  }
}
