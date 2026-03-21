terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    # bucket は環境ごとに -backend-config で渡す
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ========================================
# Modules
# ========================================

module "networking" {
  source     = "./modules/networking"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  env        = var.env
}

module "secret_manager" {
  source     = "./modules/secret-manager"
  project_id = var.project_id
  env        = var.env
}

module "cloud_sql" {
  source            = "./modules/cloud-sql"
  project_id        = var.project_id
  region            = var.region
  env               = var.env
  db_password       = var.db_password
  vpc_network_id    = module.networking.vpc_network_id
}

module "gcs" {
  source     = "./modules/gcs"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "firestore" {
  source     = "./modules/firestore"
  project_id = var.project_id
  region     = var.region
}

module "cloud_run" {
  source              = "./modules/cloud-run"
  project_id          = var.project_id
  region              = var.region
  env                 = var.env
  service_account_email = module.iam.cloud_run_sa_email
  cloud_sql_instance  = module.cloud_sql.connection_name
  db_password_secret  = module.secret_manager.db_password_secret_id
  gcs_bucket          = module.gcs.media_bucket_name
}

module "load_balancer" {
  source           = "./modules/load-balancer"
  project_id       = var.project_id
  region           = var.region
  env              = var.env
  cloud_run_service = module.cloud_run.service_name
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  region     = var.region
  env        = var.env
}

module "workflows" {
  source                = "./modules/workflows"
  project_id            = var.project_id
  region                = var.region
  env                   = var.env
  service_account_email = module.iam.workflows_sa_email
}
