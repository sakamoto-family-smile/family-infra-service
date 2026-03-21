# Cloud Run サービスアカウント
resource "google_service_account" "cloud_run" {
  account_id   = "family-app-cloud-run-${var.env}"
  display_name = "Family App Cloud Run SA (${var.env})"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_run_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_tasks" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_firebase" {
  project = var.project_id
  role    = "roles/firebase.sdkAdminServiceAgent"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Workflows サービスアカウント
resource "google_service_account" "workflows" {
  account_id   = "family-app-workflows-${var.env}"
  display_name = "Family App Workflows SA (${var.env})"
  project      = var.project_id
}

resource "google_project_iam_member" "workflows_run" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.workflows.email}"
}

resource "google_project_iam_member" "workflows_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.workflows.email}"
}

resource "google_project_iam_member" "workflows_firestore" {
  project = var.project_id
  role    = "roles/datastore.importExportAdmin"
  member  = "serviceAccount:${google_service_account.workflows.email}"
}

# Cloud Functions サービスアカウント
resource "google_service_account" "functions" {
  account_id   = "family-app-functions-${var.env}"
  display_name = "Family App Cloud Functions SA (${var.env})"
  project      = var.project_id
}

resource "google_project_iam_member" "functions_firebase" {
  project = var.project_id
  role    = "roles/firebase.sdkAdminServiceAgent"
  member  = "serviceAccount:${google_service_account.functions.email}"
}

resource "google_project_iam_member" "functions_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.functions.email}"
}
