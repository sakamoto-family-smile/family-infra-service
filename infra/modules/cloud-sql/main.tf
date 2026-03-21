resource "google_sql_database_instance" "main" {
  name             = "family-app-db-${var.env}"
  database_version = "POSTGRES_16"
  region           = var.region
  project          = var.project_id

  deletion_protection = var.env == "prod" ? true : false

  settings {
    tier              = var.env == "prod" ? "db-custom-1-3840" : "db-f1-micro"
    availability_type = var.env == "prod" ? "REGIONAL" : "ZONAL"
    disk_autoresize   = true
    disk_size         = 10

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.env == "prod"
      start_time                     = "02:00"
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
    }

    insights_config {
      query_insights_enabled = true
    }

    database_flags {
      name  = "max_connections"
      value = var.env == "prod" ? "100" : "25"
    }
  }
}

resource "google_sql_database" "app" {
  name     = "family_app"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

resource "google_sql_user" "app" {
  name     = "family_app"
  instance = google_sql_database_instance.main.name
  password = var.db_password
  project  = var.project_id
}
