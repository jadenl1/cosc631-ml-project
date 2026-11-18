#!/usr/bin/env bash
set -euo pipefail

PROJECT=book-genre-classifier-515119
REGION=us-east1
BUCKET="${PROJECT}-book-genre-private"
IMAGE="$REGION-docker.pkg.dev/$PROJECT/book-genre-images/training:latest"
if [[ "$(gcloud config get-value project 2>/dev/null)" != "$PROJECT" ]]; then
  echo "Select project $PROJECT first." >&2
  exit 1
fi

gcloud builds submit --project="$PROJECT" --region="$REGION" --config=cloudbuild.training.yaml .
gcloud run jobs deploy book-genre-training \
  --project="$PROJECT" \
  --region="$REGION" \
  --image="$IMAGE" \
  --service-account="book-genre-training@$PROJECT.iam.gserviceaccount.com" \
  --set-env-vars="BUCKET_NAME=$BUCKET" \
  --cpu=2 \
  --memory=2Gi \
  --task-timeout=1800 \
  --max-retries=0
gcloud run jobs execute book-genre-training --project="$PROJECT" --region="$REGION" --wait
gcloud storage ls "gs://$BUCKET/models/latest/model.joblib" "gs://$BUCKET/models/latest/evaluation.json"
