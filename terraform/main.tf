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

resource "google_storage_bucket" "cloudbuild_logs_bucket" {
  name          = "cloudbuild-logs-bucket"
  location      = "europe-west2"
  force_destroy = true
}

# Create a Google Cloud Storage bucket for Dataflow staging and temp files
resource "google_storage_bucket" "dataflow_bucket" {
  name          = "parallel-transcriber-dataflow-bucket"
  location      = "europe-west2"
  force_destroy = true
}

# Create a Service Account for Dataflow
resource "google_service_account" "dataflow_service_account" {
  account_id   = "dataflow-service-account"
  display_name = "Dataflow Service Account"
}

# Grant the service account Dataflow Worker permissions
resource "google_project_iam_member" "dataflow_worker_role" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

# Grant the service account permissions to read/write to Google Cloud Storage
resource "google_project_iam_member" "storage_object_admin_role" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.email}"
}

# Create a Dataflow job
#resource "google_dataflow_job" "dataflow_job" {
#  depends_on = [
#    google_storage_bucket.dataflow_bucket,
#    google_service_account.dataflow_service_account,
#    google_project_iam_member.dataflow_worker_role,
#    google_project_iam_member.storage_object_admin_role
#  ]

#  name                  = "parallel-transcriber-dataflow-job"
#  template_gcs_path     = "gs://${google_storage_bucket.dataflow_bucket.name}/templates/parallel_transcriber_template"
#  temp_gcs_location     = "gs://${google_storage_bucket.dataflow_bucket.name}/temp"
#  region                = "europe-west2"
#  service_account_email = google_service_account.dataflow_service_account.email
#  on_delete             = "cancel"
#}
