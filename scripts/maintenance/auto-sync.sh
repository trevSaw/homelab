#!/bin/bash
# Auto-sync Personal repo to GitHub
# Runs daily via cron

REPO_DIR="$HOME/my_projects/Personal"
LOG_FILE="$HOME/.local/log/personal-sync.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Timestamp for logging
echo "=== Sync started: $(date) ===" >> "$LOG_FILE"

cd "$REPO_DIR" || {
    echo "ERROR: Could not cd to $REPO_DIR" >> "$LOG_FILE"
    exit 1
}

# Check if there are any changes
if [[ -z $(git status --porcelain) ]]; then
    echo "No changes to sync" >> "$LOG_FILE"
    echo "=== Sync completed: $(date) ===" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    exit 0
fi

# Stage all changes
git add -A >> "$LOG_FILE" 2>&1

# Commit with timestamp
COMMIT_MSG="Auto-sync: $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

# Pull first (in case of remote changes)
git pull --rebase >> "$LOG_FILE" 2>&1

# Push to remote
git push >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Push successful" >> "$LOG_FILE"
else
    echo "ERROR: Push failed" >> "$LOG_FILE"
fi

echo "=== Sync completed: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
