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

# Create a Dataflow job using the custom Docker image
resource "google_dataflow_flex_template_job" "dataflow_job" {
  name                  = "parallel-transcriber-dataflow-job"
  project               = var.project_id
  location              = "europe-west2"
  container_image       = "gcr.io/${var.project_id}/dataflow-transcriber-image:latest"
  service_account_email = google_service_account.dataflow_service_account.email

  on_delete = "cancel"

  parameters = {
    # Add any necessary parameters for your job, if applicable
    input_param  = "value1"
    output_param = "value2"
  }

  environment = {
    temp_gcs_location = "gs://${google_storage_bucket.dataflow_bucket.name}/temp"
    # Additional environment variables if needed
  }
}
