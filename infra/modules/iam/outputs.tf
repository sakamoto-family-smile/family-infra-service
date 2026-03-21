output "cloud_run_sa_email"  { value = google_service_account.cloud_run.email }
output "workflows_sa_email"  { value = google_service_account.workflows.email }
output "functions_sa_email"  { value = google_service_account.functions.email }
