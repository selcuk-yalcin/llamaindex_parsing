#!/bin/bash
cd /Users/selcuk/Desktop/Deep\ Learning\ assignment/Pinecone/semantic_search

echo "=== Current Directory ==="
pwd

echo -e "\n=== Git Status ==="
git status

echo -e "\n=== Adding Files ==="
git add .

echo -e "\n=== Committing Changes ==="
git commit -m "Semantic search with Pinecone: notebook, data cleaning, API keys management"

echo -e "\n=== Checking Remote ==="
git remote -v

echo -e "\n=== Pushing to GitHub ==="
git push -u origin main

echo -e "\n=== Push Complete ==="
