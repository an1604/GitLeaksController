module "artifact_repository" {

  source                   = "globe.jfrog.io/hmd-terraform-local__gcp/terraform-gcp-artifact-registry/gcp"

  version                  = "v0.1.1"

  for_each                 = local.artifact_repositories

  project_id               = each.value.project_id

  repository_id            = each.value.repository_id

  location                 = each.value.location

  format                   = each.value.format

  mode                     = each.value.mode

  remote_repository_config = each.value.remote_repository_config

  kms_key_name             = each.value.kms_key_name

}
