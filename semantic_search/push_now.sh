#!/bin/bash

# Set directory
DIR="/Users/selcuk/Desktop/Deep Learning assignment/Pinecone/semantic_search"
cd "$DIR"

# Git operations
echo "Adding files..."
git add .

echo "Committing..."
git commit -m "Add semantic search with Pinecone integration"

echo "Pulling latest..."
git pull origin main --rebase 2>&1 || true

echo "Pushing..."
git push -u origin main

echo "Done!"
