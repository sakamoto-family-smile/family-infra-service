variable "project_id"     { type = string }
variable "region"         { type = string }
variable "env"            { type = string }
variable "db_password"    { type = string; sensitive = true }
variable "vpc_network_id" { type = string }
