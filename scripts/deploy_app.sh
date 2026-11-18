#!/usr/bin/env bash
set -euo pipefail
PROJECT=book-genre-classifier-515119
REGION=us-east1
BUCKET="${PROJECT}-book-genre-private"
IMAGE="$REGION-docker.pkg.dev/$PROJECT/book-genre-images/app:latest"
[[ "$(gcloud config get-value project 2>/dev/null)" == "$PROJECT" ]] || { echo "Select project $PROJECT first." >&2; exit 1; }
mkdir -p artifacts
gcloud storage cp "gs://$BUCKET/models/latest/model.joblib" artifacts/model.joblib
gcloud builds submit --project="$PROJECT" --region="$REGION" --config=cloudbuild.app.yaml .
gcloud run deploy book-genre-predictor --project="$PROJECT" --region="$REGION" --image="$IMAGE" --service-account="book-genre-app@$PROJECT.iam.gserviceaccount.com" --allow-unauthenticated --min-instances=0 --max-instances=2 --cpu=1 --memory=1Gi --no-cpu-boost --port=8080
