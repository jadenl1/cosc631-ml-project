#!/usr/bin/env bash
set -euo pipefail

PROJECT=book-genre-classifier-515119
REGION=us-east1
BUCKET="${PROJECT}-book-genre-private"
REPO=book-genre-images
if [[ "$(gcloud config get-value project 2>/dev/null)" != "$PROJECT" ]]; then
  echo "Select project $PROJECT first." >&2
  exit 1
fi

if [[ "$(gcloud billing projects describe "$PROJECT" --format='value(billingEnabled)')" != True ]]; then
  echo "Billing is not enabled." >&2
  exit 1
fi

gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com storage.googleapis.com iam.googleapis.com \
  --project="$PROJECT"
if ! gcloud storage buckets describe "gs://$BUCKET" --project="$PROJECT" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://$BUCKET" --project="$PROJECT" --location="$REGION" --uniform-bucket-level-access --public-access-prevention
fi
if ! gcloud artifacts repositories describe "$REPO" --location="$REGION" --project="$PROJECT" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPO" --repository-format=docker --location="$REGION" --project="$PROJECT"
fi
for account in book-genre-training book-genre-app; do
  if ! gcloud iam service-accounts describe "$account@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$account" --project="$PROJECT"
  fi
done
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" \
  --member="serviceAccount:book-genre-training@$PROJECT.iam.gserviceaccount.com" \
  --role=roles/storage.objectUser \
  --condition=None \
  --quiet
gcloud storage cp data/raw/data.csv "gs://$BUCKET/data/raw/data.csv"
