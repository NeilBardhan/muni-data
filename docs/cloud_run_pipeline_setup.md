# Google Cloud Run + GitHub Actions Pipeline Setup

## Overview

This document describes how to securely deploy a Python data pipeline from GitHub to Google Cloud Run.
The pipeline queries an external API, stores raw JSON data in Google Cloud Storage, and loads transformed data into BigQuery.

Key services used:

* **Cloud Run** – executes the Python API ingestion container.
* **Secret Manager** – stores external API keys and credentials.
* **Artifact Registry** – hosts the container images.
* **Workload Identity Federation (WIF)** – lets GitHub Actions deploy without storing GCP keys.
* **BigQuery** – stores processed data.
* **Cloud Scheduler** (optional) – triggers the job on a daily schedule.

---

## 1. Prerequisites

```bash
export PROJECT_ID="sf-muni-analytics"
export REGION="us-west1"
export GITHUB_REPO="NeilBardhan/muni-data"
export SERVICE_NAME="muni-data-ingest-pipeline"
export SECRET_NAME="MUNI_API_KEY"
```

Ensure the following APIs are enabled:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iamcredentials.googleapis.com \
  iam.googleapis.com
```

---

## 2. Create Cloud Run Service Account

```bash
gcloud iam service-accounts create ${SERVICE_NAME}-sa \
  --display-name "Cloud Run service account for ${SERVICE_NAME}"
```

Grant necessary permissions:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

---

## 3. Create and Populate the API Secret

```bash
gcloud secrets create $SECRET_NAME --replication-policy="automatic"
echo -n "your-api-key-here" | gcloud secrets versions add $SECRET_NAME --data-file=-
```

---

## 4. Set Up Workload Identity Federation (WIF)

Create a WIF pool and provider:

```bash
gcloud iam workload-identity-pools create github-pool \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"
```

Grant GitHub repository impersonation access:

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
  ${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository:${GITHUB_REPO}"
```

---

## 5. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create muni-data-ingest-pipeline \
  --repository-format=docker \
  --location=$REGION \
  --description="Container images for ${SERVICE_NAME}"
```

---

## 6. Initial Cloud Run Deployment

```bash
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/muni-data-ingest-pipeline/muni-data-ingest-pipeline:latest \
  --region $REGION \
  --service-account ${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --update-secrets API_KEY=${SECRET_NAME}:latest
```

Your Python code can access the secret as:

```python
import os
api_key = os.getenv("API_KEY")
```

---

## 7. Configure GitHub Secrets

Add the following repository secrets under
**Settings → Secrets and Variables → Actions**:

| Secret Name        | Value                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| `GCP_PROJECT_ID`   | `$PROJECT_ID`                                                                                             |
| `GCP_SA_EMAIL`     | `${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com`                                                |
| `GCP_WIF_PROVIDER` | `projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |

---

## 8. GitHub Actions Workflow Example

Save as `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
          service_account: ${{ secrets.GCP_SA_EMAIL }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker ${{ secrets.GCP_PROJECT_ID }}-docker.pkg.dev

      - name: Build and push container
        run: |
          IMAGE=${{ secrets.GCP_PROJECT_ID }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/muni-data-ingest-pipeline/muni-data-ingest-pipeline
          docker build -t $IMAGE .
          docker push $IMAGE

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy muni-data-ingest-pipeline \
            --image ${{ secrets.GCP_PROJECT_ID }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/muni-data-ingest-pipeline/muni-data-ingest-pipeline \
            --region us-central1 \
            --allow-unauthenticated \
            --update-secrets API_KEY=MUNI_API_KEY:latest
```

---

## 9. Optional: Cloud Storage Lifecycle Policy

If the pipeline writes raw JSON to GCS, set a lifecycle rule to delete old data automatically:

```bash
cat > lifecycle.json <<EOF
{
  "rule": [
    {
      "action": { "type": "Delete" },
      "condition": { "age": 90 }
    }
  ]
}
EOF

gsutil lifecycle set lifecycle.json gs://my-raw-data-bucket
```

---

## 10. Verification

Check Cloud Run and secret access:

```bash
gcloud run services describe $SERVICE_NAME --region $REGION
gcloud secrets get-iam-policy $SECRET_NAME
```

---

## Summary

| Component                    | Purpose                                       |
| ---------------------------- | --------------------------------------------- |
| Cloud Run                    | Executes Python ingestion container           |
| Secret Manager               | Stores API key securely                       |
| Artifact Registry            | Hosts container images                        |
| Workload Identity Federation | Authenticates GitHub Actions without GCP keys |
| BigQuery                     | Stores transformed data                       |
| Cloud Storage                | Holds raw JSON snapshots                      |
| Lifecycle Rules              | Manage cost and data retention                |

This configuration enables a fully automated, secure data ingestion and transformation pipeline from GitHub to GCP.
