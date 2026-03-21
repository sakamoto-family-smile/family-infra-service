# Cloud Run に対する外部 HTTPS Load Balancer

resource "google_compute_global_address" "default" {
  name    = "family-app-lb-ip-${var.env}"
  project = var.project_id
}

resource "google_compute_managed_ssl_certificate" "default" {
  name    = "family-app-cert-${var.env}"
  project = var.project_id

  managed {
    domains = ["api.family-app.example.com"]  # 実際のドメインに変更
  }
}

resource "google_compute_backend_service" "api" {
  name                  = "family-app-backend-${var.env}"
  project               = var.project_id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTP"

  backend {
    group = google_compute_region_network_endpoint_group.cloud_run.id
  }

  security_policy = google_compute_security_policy.cloud_armor.id
}

resource "google_compute_region_network_endpoint_group" "cloud_run" {
  name                  = "family-app-neg-${var.env}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id

  cloud_run {
    service = var.cloud_run_service
  }
}

resource "google_compute_url_map" "default" {
  name            = "family-app-url-map-${var.env}"
  project         = var.project_id
  default_service = google_compute_backend_service.api.id
}

resource "google_compute_target_https_proxy" "default" {
  name             = "family-app-https-proxy-${var.env}"
  project          = var.project_id
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

resource "google_compute_global_forwarding_rule" "default" {
  name                  = "family-app-forwarding-rule-${var.env}"
  project               = var.project_id
  ip_address            = google_compute_global_address.default.id
  port_range            = "443"
  target                = google_compute_target_https_proxy.default.id
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# Cloud Armor セキュリティポリシー
resource "google_compute_security_policy" "cloud_armor" {
  name    = "family-app-armor-${var.env}"
  project = var.project_id

  # レート制限 (IP あたり 100 req/min)
  rule {
    action   = "throttle"
    priority = 1000
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
    }
    description = "Rate limiting"
  }

  # デフォルト許可
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow"
  }
}
