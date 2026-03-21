resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "firebase_project_id" {
  secret_id = "firebase-project-id"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gcs_bucket" {
  secret_id = "gcs-bucket"
  project   = var.project_id

  replication {
    auto {}
  }
}
