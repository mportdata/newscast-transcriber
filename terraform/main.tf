# Configure the Google provider
provider "google" {
  project = "parallel-audio-transcriber"
  region  = "europe-west2" # Change this to your region
}

# Create a Google Cloud Storage bucket for Dataflow staging and temp files
resource "google_storage_bucket" "dataflow_bucket" {
  name          = "parallel-transcriber-dataflow-stage" # Make sure this is unique globally
  location      = "EUROPE-WEST2"
  force_destroy = true # Optional: allows Terraform to delete the bucket when running `terraform destroy`
}

# Create a Dataflow job
resource "google_dataflow_job" "dataflow_job" {
  name              = "parallel-transcriber-dataflow-job"
  template_gcs_path = "gs://${google_storage_bucket.dataflow_bucket.name}/templates/your-template"
  temp_gcs_location = "gs://${google_storage_bucket.dataflow_bucket.name}/temp"
  region            = "europe-west2"

<<<<<<< Updated upstream
  //  parameters = {
  //    input  = "gs://your-input-data-path/input.txt"
  //    output = "gs://your-output-data-path/output.txt"
  //  }

=======
>>>>>>> Stashed changes
  on_delete = "cancel" # Cancels the Dataflow job when Terraform destroys resources
}
