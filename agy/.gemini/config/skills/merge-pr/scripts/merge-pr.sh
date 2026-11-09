#!/usr/bin/env bash
set -euo pipefail

# Helper script for merge-pr skill.
# Fetches base branch and PR branch, merges PR into base branch (main/master).
# Resolves or reports conflicts for agent resolution.

REPO_DIR="."
PR_TARGET=""
BASE_BRANCH=""
STRATEGY="merge"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_DIR="$2"
      shift 2
      ;;
    --pr)
      PR_TARGET="$2"
      shift 2
      ;;
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --squash)
      STRATEGY="squash"
      shift
      ;;
    --merge)
      STRATEGY="merge"
      shift
      ;;
    -h|--help)
      echo "Usage: merge-pr.sh [--repo <path>] [--pr <number>] [--base <base_branch>] [--squash|--merge]"
      exit 0
      ;;
    *)
      if [[ -z "$PR_TARGET" ]]; then
        PR_TARGET="$1"
      fi
      shift
      ;;
  esac
done

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository: $REPO_DIR" >&2
  exit 1
fi

# Require PR target
if [[ -z "$PR_TARGET" ]]; then
  echo "ERROR: PR number required. Usage: merge-pr.sh <pr_number>" >&2
  exit 1
fi

# Ensure clean working tree
if ! git diff --quiet || ! git diff --staged --quiet; then
  echo "ERROR: Working tree has uncommitted changes. Stash or commit before merging." >&2
  exit 2
fi

# Query PR metadata via gh
PR_TITLE=""
HEAD_BRANCH=""
if command -v gh >/dev/null 2>&1; then
  PR_JSON=$(gh pr view "$PR_TARGET" --json number,title,headRefName,baseRefName,state 2>/dev/null | cat || true)
  if [[ -n "$PR_JSON" ]]; then
    PR_STATE=$(echo "$PR_JSON" | grep -o '"state":"[^"]*"' | cut -d'"' -f4 || echo "OPEN")
    if [[ "$PR_STATE" != "OPEN" ]]; then
      echo "ERROR: PR #$PR_TARGET is not OPEN (current state: $PR_STATE)." >&2
      exit 1
    fi
    HEAD_BRANCH=$(echo "$PR_JSON" | grep -o '"headRefName":"[^"]*"' | cut -d'"' -f4)
    PR_TITLE=$(echo "$PR_JSON" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
    if [[ -z "$BASE_BRANCH" ]]; then
      BASE_BRANCH=$(echo "$PR_JSON" | grep -o '"baseRefName":"[^"]*"' | cut -d'"' -f4)
    fi
  fi
fi

if [[ -z "$HEAD_BRANCH" ]]; then
  HEAD_BRANCH="$PR_TARGET"
fi

# Fallback base branch detection
if [[ -z "$BASE_BRANCH" ]]; then
  BASE_REF=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -n "$BASE_REF" ]]; then
    BASE_BRANCH="${BASE_REF#refs/remotes/origin/}"
  elif git show-ref --verify --quiet refs/remotes/origin/main || git show-ref --verify --quiet refs/heads/main; then
    BASE_BRANCH="main"
  elif git show-ref --verify --quiet refs/remotes/origin/master || git show-ref --verify --quiet refs/heads/master; then
    BASE_BRANCH="master"
  else
    BASE_BRANCH="main"
  fi
fi

echo "Fetching remote branches: $BASE_BRANCH and $HEAD_BRANCH..."
git fetch origin "$BASE_BRANCH"
git fetch origin "$HEAD_BRANCH" || true

echo "Checking out base branch: $BASE_BRANCH..."
git checkout "$BASE_BRANCH"
git pull --ff-only origin "$BASE_BRANCH" || true

echo "Merging PR #$PR_TARGET ($HEAD_BRANCH) into $BASE_BRANCH..."
if [[ "$STRATEGY" == "squash" ]]; then
  if git merge --squash "origin/$HEAD_BRANCH"; then
    echo "SUCCESS: Clean squash merge. Ready to commit and run verification."
    exit 0
  fi
else
  MERGE_MSG="Merge pull request #$PR_TARGET from $HEAD_BRANCH"
  if [[ -n "${PR_TITLE:-}" ]]; then
    MERGE_MSG="$MERGE_MSG

$PR_TITLE"
  fi
  if git merge "origin/$HEAD_BRANCH" --no-ff -m "$MERGE_MSG"; then
    echo "SUCCESS: Clean merge of PR #$PR_TARGET into $BASE_BRANCH."
    exit 0
  fi
fi

echo "CONFLICT: Merge conflicts detected merging $HEAD_BRANCH into $BASE_BRANCH." >&2
git diff --name-only --diff-filter=U >&2
exit 3
