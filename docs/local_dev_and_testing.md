## Local Development & Testing

### 1. Running Locally with a Local `.env` File

For local testing, you can provide your API key via a `.env` file instead of Secret Manager.

Create a file named `.env` in your project root:

```
API_KEY=your-api-key-here
PROJECT_ID=your-project-id
```

Make sure `.env` is **ignored** in your `.gitignore`:

```
.env
```

You can load environment variables automatically with `python-dotenv` during local testing:

```bash
pip install python-dotenv
```

Example snippet in your Python code:

```python
from dotenv import load_dotenv
import os
import requests

load_dotenv()  # only used locally

def fetch_data():
    api_key = os.getenv("API_KEY")
    url = "https://example.com/api/data"
    resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
    return resp.json()
```

---

### 2. Running the Docker Container Locally

You can also test your containerized app using the same API key from the `.env` file.

First, build the Docker image:

```bash
docker build -t muni-data-ingest-pipeline-local .
```

Then run it with environment variables loaded:

```bash
docker run --rm --env-file .env muni-data-ingest-pipeline-local
```

If you’re using Flask or FastAPI for your ingestion logic, you can test endpoints locally:

```bash
docker run -p 8080:8080 --env-file .env muni-data-ingest-pipeline-local
```

Visit:

```
http://localhost:8080
```

---

### 3. Simulating Cloud Run Behavior Locally

To closely match Cloud Run runtime:

```bash
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e PROJECT_ID=$PROJECT_ID \
  -e API_KEY=$API_KEY \
  muni-data-ingest-pipeline-local
```

This mirrors the environment Cloud Run uses for environment variables and port bindings.

---

### 4. Testing with Emulated GCP Services (Optional)

If your code interacts with GCP resources like GCS or BigQuery, you can authenticate locally using your gcloud user credentials:

```bash
gcloud auth application-default login
```

Then run your container with your local credentials mounted:

```bash
docker run -v ~/.config/gcloud:/root/.config/gcloud --env-file .env muni-data-ingest-pipeline-local
```

Your application will pick up your `Application Default Credentials` as if it were running inside GCP.

---

### 5. Cleanup After Testing

When done testing:

```bash
docker image rm muni-data-ingest-pipeline-local
```

If you’ve created any temporary files (like `.env`), ensure they’re excluded from Git commits.

---

### Summary

| Goal                         | Local Testing Method                       |
| ---------------------------- | ------------------------------------------ |
| Run app locally with secrets | `.env` file + `python-dotenv`              |
| Test containerized behavior  | `docker run --env-file .env`               |
| Emulate GCP credentials      | `gcloud auth application-default login`    |
| Match Cloud Run runtime      | `docker run -p 8080:8080 -e PORT=8080 ...` |

This setup ensures you can iterate and debug your ingestion pipeline safely and quickly before pushing to GitHub or deploying to Cloud Run.
