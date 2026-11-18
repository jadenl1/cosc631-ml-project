#!/usr/bin/env bash
set -euo pipefail

PROJECT=book-genre-classifier-515119
REGION=us-east1
BUCKET="${PROJECT}-book-genre-private"
if [[ "$(gcloud config get-value project 2>/dev/null)" != "$PROJECT" ]]; then
  echo "Select project $PROJECT first." >&2
  exit 1
fi

echo "This deletes the book-genre-predictor service, book-genre-training job, book-genre-images repository and its images, gs://$BUCKET and all objects, and the book-genre-training and book-genre-app service accounts."
read -r -p 'Type DELETE to continue: ' answer
[[ "$answer" == DELETE ]] || exit 1
gcloud run services delete book-genre-predictor --project="$PROJECT" --region="$REGION" --quiet
gcloud run jobs delete book-genre-training --project="$PROJECT" --region="$REGION" --quiet
gcloud artifacts repositories delete book-genre-images --project="$PROJECT" --location="$REGION" --quiet
gcloud storage rm --recursive "gs://$BUCKET"
for account in book-genre-training book-genre-app; do
  gcloud iam service-accounts delete "$account@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" --quiet
done
