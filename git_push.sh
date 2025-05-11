#!/bin/bash

# Check if a commit message was provided
if [ -z "$1" ]; then
  echo "Error: Please provide a commit message."
  echo "Usage: ./git_push.sh \"Your commit message\""
  exit 1
fi

# Pull the latest changes first (optional, but good practice)
echo "Pulling latest changes..."
git pull

# Add all changes
echo "Adding changes..."
git add .

# Commit with the provided message
echo "Committing with message: $1"
git commit -m "$1"

# Push to GitHub
echo "Pushing to GitHub..."
git push

echo "Done! Changes have been pushed to GitHub."