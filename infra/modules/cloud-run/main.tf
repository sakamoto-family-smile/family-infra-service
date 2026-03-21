resource "google_cloud_run_v2_service" "api" {
  name     = "family-app-api-${var.env}"
  location = var.region
  project  = var.project_id

  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.env == "prod" ? 1 : 0
      max_instance_count = var.env == "prod" ? 10 : 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/family-app/family-app-api:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      ports {
        container_port = 8080
      }

      env {
        name  = "ENV"
        value = var.env
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "CLOUD_SQL_INSTANCE"
        value = var.cloud_sql_instance
      }

      env {
        name  = "GCS_BUCKET"
        value = var.gcs_bucket
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.db_password_secret
            version = "latest"
          }
        }
      }
    }

    vpc_access {
      egress = "PRIVATE_RANGES_ONLY"
    }
  }
}

# Cloud Run Jobs: DB Migration
resource "google_cloud_run_v2_job" "db_migrate" {
  name     = "db-migrate-${var.env}"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = var.service_account_email

      containers {
        image   = "${var.region}-docker.pkg.dev/${var.project_id}/family-app/family-app-api:latest"
        command = ["uv", "run", "alembic", "upgrade", "head"]

        env {
          name  = "ENV"
          value = var.env
        }
        env {
          name  = "CLOUD_SQL_INSTANCE"
          value = var.cloud_sql_instance
        }
        env {
          name = "DB_PASSWORD"
          value_source {
            secret_key_ref {
              secret  = var.db_password_secret
              version = "latest"
            }
          }
        }
      }
    }
  }
}

# Cloud Tasks キュー
resource "google_cloud_tasks_queue" "main" {
  name     = "family-app-tasks-${var.env}"
  location = var.region
  project  = var.project_id

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 100
  }

  retry_config {
    max_attempts  = 5
    max_backoff   = "3600s"
    min_backoff   = "10s"
    max_doublings = 4
  }
}
