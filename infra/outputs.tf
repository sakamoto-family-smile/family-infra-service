output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = module.cloud_run.service_url
}

output "load_balancer_ip" {
  description = "Load Balancer external IP"
  value       = module.load_balancer.external_ip
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name"
  value       = module.cloud_sql.connection_name
}

output "media_bucket_name" {
  description = "GCS media bucket name"
  value       = module.gcs.media_bucket_name
}

output "cloud_run_sa_email" {
  description = "Cloud Run service account email"
  value       = module.iam.cloud_run_sa_email
}
