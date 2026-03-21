output "db_password_secret_id"     { value = google_secret_manager_secret.db_password.secret_id }
output "firebase_project_secret_id" { value = google_secret_manager_secret.firebase_project_id.secret_id }
