resource "google_workflows_workflow" "daily_dbt_pipeline" {
  name            = "daily-dbt-pipeline-${var.env}"
  region          = var.region
  project         = var.project_id
  service_account = var.service_account_email
  source_contents = file("${path.root}/../data-platform/workflows/workflow_daily_dbt_run.yaml")
}

resource "google_cloud_scheduler_job" "daily_dbt_trigger" {
  name      = "daily-dbt-trigger-${var.env}"
  region    = var.region
  project   = var.project_id
  schedule  = "0 21 * * *"  # UTC 21:00 = JST 06:00
  time_zone = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/projects/${var.project_id}/locations/${var.region}/workflows/${google_workflows_workflow.daily_dbt_pipeline.name}/executions"
    body        = base64encode("{\"argument\": \"{\\\"env\\\": \\\"${var.env}\\\"}\"}")

    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}
