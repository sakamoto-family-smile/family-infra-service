# BigQuery データセット

resource "google_bigquery_dataset" "raw_cloud_sql" {
  dataset_id  = "raw_cloud_sql"
  location    = var.region
  project     = var.project_id
  description = "Cloud SQL からのローエクスポートデータ"

  default_partition_expiration_ms = null
  delete_contents_on_destroy      = var.env == "dev"
}

resource "google_bigquery_dataset" "raw_firestore" {
  dataset_id  = "raw_firestore"
  location    = var.region
  project     = var.project_id
  description = "Firestore からのローエクスポートデータ"

  delete_contents_on_destroy = var.env == "dev"
}

resource "google_bigquery_dataset" "dbt_staging" {
  dataset_id  = "staging"
  location    = var.region
  project     = var.project_id
  description = "dbt staging models"

  delete_contents_on_destroy = var.env == "dev"
}

resource "google_bigquery_dataset" "dbt_marts" {
  dataset_id  = "marts"
  location    = var.region
  project     = var.project_id
  description = "dbt marts models"

  delete_contents_on_destroy = var.env == "dev"
}

resource "google_bigquery_dataset" "dbt_reports" {
  dataset_id  = "reports"
  location    = var.region
  project     = var.project_id
  description = "dbt report models"

  delete_contents_on_destroy = var.env == "dev"
}
