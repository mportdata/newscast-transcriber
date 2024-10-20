# Define the provider and backend as before
provider "google" {
  project = var.project_id
  region  = "europe-west2"
}

terraform {
  backend "gcs" {
    bucket = "terraform-state-newscast-transcriber"
    prefix = "terraform/state"
  }
}

# Create the required Google Storage Buckets and Service Accounts as before
resource "google_storage_bucket" "cloudbuild_logs_bucket" {
  name          = "cloudbuild-logs-bucket-newscast-transcriber"
  location      = "europe-west2"
  force_destroy = true
}

resource "google_storage_bucket" "dataflow_bucket" {
  name          = "parallel-transcriber-dataflow-bucket"
  location      = "europe-west2"
  force_destroy = true
}

resource "google_service_account" "dataflow_service_account" {
  account_id   = "dataflow-service-account"
  display_name = "Dataflow Service Account"
}

resource "google_project_iam_member" "dataflow_worker_role" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

resource "google_project_iam_member" "storage_object_admin_role" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

# Define the Dataflow job using google_dataflow_job
resource "google_dataflow_job" "dataflow_job" {
  name                  = "parallel-transcriber-dataflow-job"
  project               = var.project_id
  region                = "europe-west2"
  service_account_email = google_service_account.dataflow_service_account.email

  # Define the container image
  container_spec_gcs_path = "gs://${google_storage_bucket.dataflow_bucket.name}/container_spec.json"

  on_delete = "cancel"

  # Set up environment variables and configuration
  environment = {
    temp_gcs_location = "gs://${google_storage_bucket.dataflow_bucket.name}/temp"
  }
}
