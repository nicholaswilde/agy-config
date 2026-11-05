---
trigger: always_on
description: "GitHub issue creation, labels, and issue closing rules"
---

# GitHub Issues Workflow for Tasks

Strict workflow rule for task management, bug tracking, and feature development.

## Rule

For features, enhancements, and bugs:

1. **Use Remote GitHub Issues Directly**:
   - Manage, track, and update requirements via remote GitHub issues using `gh` (`rtk gh issue ... | cat`).
   - Do NOT create or maintain local Conductor tracks (`.agents/conductor/tracks/`, `plan.md`, `spec.md`, `tracks.md`).
2. **Issue Interaction**:
   - Query: `rtk gh issue list | cat`
   - View details: `rtk gh issue view <issue> | cat`
   - Create when needed: `rtk gh issue create --title "<title>" --body "<body>" --label "<bug|enhancement>" | cat`
   - Close: Include `Fixes #<number>` in commit messages or use `rtk gh issue close <number>`.
3. **Commit Linking**:
   - GitHub issues only close automatically when commits containing `Fixes #<issue>` are pushed to the remote repository.
