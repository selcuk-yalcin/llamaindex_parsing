#!/bin/bash
cd "/Users/selcuk/Desktop/Deep Learning assignment/Pinecone/semantic_search"

echo "=== Git Pull ===" 
git pull origin main --rebase 2>&1

echo ""
echo "=== Git Push ===" 
git push origin main 2>&1

echo ""
echo "=== Status ===" 
git status 2>&1

echo ""
echo "=== Last Commits ===" 
git log --oneline -5 2>&1
