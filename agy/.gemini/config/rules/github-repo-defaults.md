---
trigger: always_on
description: "Configure default GitHub repo settings on new repo creation"
---

# GitHub Repo Default Settings

## Rule

When creating a new GitHub repository (`gh repo create`), always apply these defaults:

1. **Disable Wiki & Enable Auto-Delete Head Branches**:

   ```bash
   rtk gh repo edit <owner>/<repo> --enable-wiki=false --delete-branch-on-merge | cat
   ```

2. **Enable Sponsorships (`.github/FUNDING.yml`)**:
   - Create `.github/FUNDING.yml` on default branch:

     ```yaml
     ---
     github: nicholaswilde
     ```

   - GitHub API has no checkbox toggle for Sponsorships; remind user to check **Settings -> Features -> Sponsorships** if Sponsor button does not appear automatically.

## Verification

```bash
rtk gh api repos/<owner>/<repo> --jq '{has_wiki, delete_branch_on_merge}' | cat
```

Confirm `has_wiki: false` and `delete_branch_on_merge: true`.
