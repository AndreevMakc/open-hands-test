#!/bin/bash
set -e

# Set the remote URL with token
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/AndreevMakc/open-hands-test.git"

# Push the branch
git push -u origin feat/stage2-database-api-implementation

echo "Branch pushed successfully!"