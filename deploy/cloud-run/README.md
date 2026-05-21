# Google Cloud Run Deployment

This folder contains Cloud Run deployment files for the KshetraAI demo.

The deployed backend uses committed sanitized sample outputs:

```text
demo/sample_outputs/*.json
```

It does not require `datasets/processed/*.csv` in the cloud container.

## 1. Set Variables

```powershell
$PROJECT_ID="your-gcp-project-id"
$REGION="asia-south1"
$BACKEND_IMAGE="gcr.io/$PROJECT_ID/kshetraai-backend"
$FRONTEND_IMAGE="gcr.io/$PROJECT_ID/kshetraai-frontend"
```

## 2. Build And Deploy Backend

```powershell
gcloud builds submit --config deploy/cloud-run/backend.cloudbuild.yaml --substitutions _IMAGE=$BACKEND_IMAGE
gcloud run deploy kshetraai-backend --image $BACKEND_IMAGE --region $REGION --allow-unauthenticated --set-env-vars KSHETRA_API_DATA_MODE=sample,KSHETRA_CORS_ORIGINS=*
```

After deployment, copy the backend service URL.

Test:

```text
https://YOUR-BACKEND-URL/health
https://YOUR-BACKEND-URL/docs
```

## 3. Build And Deploy Frontend

Replace `YOUR-BACKEND-URL` with the backend Cloud Run URL.

```powershell
$BACKEND_URL="https://YOUR-BACKEND-URL"
gcloud builds submit --config deploy/cloud-run/frontend.cloudbuild.yaml --substitutions _IMAGE=$FRONTEND_IMAGE,_API_BASE_URL=$BACKEND_URL
gcloud run deploy kshetraai-frontend --image $FRONTEND_IMAGE --region $REGION --allow-unauthenticated
```

After deployment, copy the frontend service URL.

## 4. Tighten Backend CORS

Replace `YOUR-FRONTEND-URL` with the frontend Cloud Run URL.

```powershell
gcloud run services update kshetraai-backend --region $REGION --set-env-vars KSHETRA_API_DATA_MODE=sample,KSHETRA_CORS_ORIGINS=https://YOUR-FRONTEND-URL
```

## Final Review Links

Use these links for submission:

```text
Frontend: https://YOUR-FRONTEND-URL
Backend API docs: https://YOUR-BACKEND-URL/docs
```
