#!/usr/bin/env bash
set -euo pipefail

# Helper script for update-pr-branch skill.
# Fetches base branch, checks safety guard, and merges base branch into PR branch.
# STRICT INVARIANT: SHALL NOT MERGE PR INTO MAIN.

REPO_DIR="."
PR_TARGET=""
BASE_BRANCH=""

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
    -h|--help)
      echo "Usage: update-pr-branch.sh [--repo <path>] [--pr <branch_or_id>] [--base <base_branch>]"
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

# Detect base branch if not explicitly provided
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

# Checkout PR target if specified
if [[ -n "$PR_TARGET" ]]; then
  if [[ "$PR_TARGET" =~ ^[0-9]+$ ]]; then
    echo "Checking out PR #$PR_TARGET via gh..."
    gh pr checkout "$PR_TARGET" | cat
  else
    echo "Checking out branch $PR_TARGET..."
    git checkout "$PR_TARGET"
  fi
fi

CURRENT_BRANCH=$(git branch --show-current)

# CRITICAL INVARIANT: NEVER RUN ON OR MERGE INTO BASE BRANCH
if [[ "$CURRENT_BRANCH" == "$BASE_BRANCH" || "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "ERROR: Refusing to run on base branch '$CURRENT_BRANCH'." >&2
  echo "This skill SHALL NOT merge into main/master. Checkout a PR branch first." >&2
  exit 1
fi

# Ensure working tree is clean before merge
if ! git diff --quiet || ! git diff --staged --quiet; then
  echo "ERROR: Working tree has uncommitted changes. Stash or commit before merging." >&2
  exit 2
fi

echo "Fetching latest origin/$BASE_BRANCH..."
git fetch origin "$BASE_BRANCH"

echo "Merging origin/$BASE_BRANCH into $CURRENT_BRANCH..."
if git merge "origin/$BASE_BRANCH" --no-edit; then
  echo "SUCCESS: Clean merge from origin/$BASE_BRANCH into $CURRENT_BRANCH."
  exit 0
else
  echo "CONFLICT: Merge conflicts detected between origin/$BASE_BRANCH and $CURRENT_BRANCH." >&2
  git diff --name-only --diff-filter=U >&2
  exit 3
fi
