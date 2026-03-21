resource "google_storage_bucket" "media" {
  name          = "family-app-media-${var.env}"
  location      = var.region
  project       = var.project_id
  force_destroy = var.env == "dev"

  uniform_bucket_level_access = true

  versioning {
    enabled = var.env == "prod"
  }

  lifecycle_rule {
    condition {
      age = 90
      matches_prefix = ["exports/"]
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "PUT", "POST"]
    response_header = ["Content-Type", "Authorization"]
    max_age_seconds = 3600
  }
}

# Terraform state バケット
resource "google_storage_bucket" "tf_state" {
  name          = "family-app-tfstate-${var.env}"
  location      = var.region
  project       = var.project_id
  force_destroy = false

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}
