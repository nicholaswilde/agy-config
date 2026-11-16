#!/usr/bin/env bash
set -euo pipefail

# Helper script for pull-and-fix skill.
# Fetches upstream, diagnoses port 22/443 SSH issues, manages working tree state,
# fast-forwards or merges remote branch, and resolves conflicts.

REPO_DIR="."
BRANCH=""
REMOTE="origin"
PREFER="none" # none | remote | local
STRATEGY="merge" # merge | rebase | ff-only

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo|-r)
      REPO_DIR="$2"
      shift 2
      ;;
    --branch|-b)
      BRANCH="$2"
      shift 2
      ;;
    --remote)
      REMOTE="$2"
      shift 2
      ;;
    --prefer-remote)
      PREFER="remote"
      shift
      ;;
    --prefer-local)
      PREFER="local"
      shift
      ;;
    --rebase)
      STRATEGY="rebase"
      shift
      ;;
    --ff-only)
      STRATEGY="ff-only"
      shift
      ;;
    -h|--help)
      echo "Usage: pull-and-fix.sh [--repo <path>] [--branch <name>] [--prefer-remote|--prefer-local] [--rebase|--ff-only]"
      exit 0
      ;;
    *)
      if [[ -d "$1" ]] && [[ "$REPO_DIR" == "." ]]; then
        REPO_DIR="$1"
      elif [[ -z "$BRANCH" ]]; then
        BRANCH="$1"
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

if [[ -z "$BRANCH" ]]; then
  BRANCH=$(git branch --show-current)
fi

if [[ -z "$BRANCH" ]]; then
  echo "ERROR: Detached HEAD state. Checkout branch before pulling." >&2
  exit 1
fi

# Step 1: Diagnose remote connectivity (SSH port 22 vs 443)
REMOTE_URL=$(git remote get-url "$REMOTE" 2>/dev/null || true)
if [[ "$REMOTE_URL" =~ github\.com ]]; then
  if ! timeout 5 git fetch --dry-run "$REMOTE" >/dev/null 2>&1; then
    echo "WARN: Remote fetch timed out or failed. Checking SSH connectivity..." >&2
    if timeout 5 ssh -T -p 443 -o ConnectTimeout=5 git@ssh.github.com 2>&1 | grep -q "successfully authenticated"; then
      echo "INFO: GitHub port 443 reachable. Setting repository core.sshCommand fallback..."
      git config core.sshCommand "ssh -p 443 -o Hostname=ssh.github.com"
    fi
  fi
fi

# Step 2: Handle uncommitted local changes
STASH_CREATED=0
if ! git diff --quiet || ! git diff --staged --quiet; then
  if [[ "$PREFER" == "remote" ]]; then
    echo "INFO: Stashing local uncommitted changes (preferring remote)..."
    git stash push -m "pull-and-fix-backup-$(date +%s)"
  else
    echo "INFO: Stashing local uncommitted changes before pull..."
    git stash push -m "pull-and-fix-autostash-$(date +%s)"
    STASH_CREATED=1
  fi
fi

# Step 3: Fetch remote tracking branch
echo "Fetching $REMOTE/$BRANCH..."
git fetch "$REMOTE" "$BRANCH"

BEHIND=$(git rev-list --count "HEAD..$REMOTE/$BRANCH" 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count "$REMOTE/$BRANCH..HEAD" 2>/dev/null || echo 0)

echo "Branch state: $AHEAD commits ahead, $BEHIND commits behind $REMOTE/$BRANCH."

if [[ "$BEHIND" -eq 0 ]]; then
  echo "SUCCESS: Branch $BRANCH is already up to date with $REMOTE/$BRANCH."
else
  if [[ "$AHEAD" -eq 0 ]]; then
    echo "Fast-forwarding to $REMOTE/$BRANCH..."
    git pull --ff-only "$REMOTE" "$BRANCH"
  elif [[ "$PREFER" == "remote" ]]; then
    echo "Resetting branch to $REMOTE/$BRANCH (--prefer-remote)..."
    git reset --hard "$REMOTE/$BRANCH"
  elif [[ "$STRATEGY" == "rebase" ]]; then
    echo "Rebasing local commits onto $REMOTE/$BRANCH..."
    if ! git rebase "$REMOTE/$BRANCH"; then
      echo "CONFLICT: Rebase conflict detected. Resolve conflicts and run 'git rebase --continue'." >&2
      exit 3
    fi
  else
    echo "Merging $REMOTE/$BRANCH into $BRANCH..."
    if ! git merge "$REMOTE/$BRANCH" -m "Merge branch '$REMOTE/$BRANCH' into $BRANCH"; then
      if [[ "$PREFER" == "local" ]]; then
        git checkout --ours .
        git add -u
        git commit -m "Merge $REMOTE/$BRANCH into $BRANCH (resolved favoring local)"
      else
        echo "CONFLICT: Merge conflict detected. Resolve conflicted files." >&2
        git diff --name-only --diff-filter=U >&2
        exit 3
      fi
    fi
  fi
fi

# Step 4: Restore stashed changes if preserved
if [[ "$STASH_CREATED" -eq 1 ]]; then
  echo "Restoring stashed changes..."
  if ! git stash pop; then
    echo "CONFLICT: Stash pop resulted in conflict. Resolve conflicted files." >&2
    exit 4
  fi
fi

# Step 5: Post-pull verification check
if [[ -f "tests/verify.sh" ]]; then
  echo "Running verification suite: tests/verify.sh..."
  bash tests/verify.sh
elif [[ -f "Taskfile.yml" ]] || [[ -f "Taskfile.yaml" ]]; then
  if task --list 2>/dev/null | grep -q "test:"; then
    echo "Running task test..."
    task test
  fi
fi

echo "SUCCESS: git pull completed and verified for $BRANCH."
exit 0
