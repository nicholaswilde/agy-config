---
trigger: always_on
description: "Split GitHub Pages Actions workflows into separate build and deploy jobs"
---

# GitHub Pages Workflow Standards

## Rule

Always split GitHub Pages workflows (`.github/workflows/docs.yml`, `pages.yml`, etc.) into separate `build` and `deploy` jobs. Never run `actions/upload-pages-artifact` and `actions/deploy-pages` in same job.

## Why

1. **Artifact Sync Race:** Running `deploy-pages` milliseconds after `upload-pages-artifact` inside one job triggers transient `Deployment failed, try again later.` errors.
2. **Idempotent Retries:** Re-running failed single-job workflow uploads second `github-pages` artifact and fails with `Multiple artifacts named "github-pages" were unexpectedly found for this workflow run`.

## Required Shape

- `permissions`: `contents: read`, `pages: write`, `id-token: write`.
- `concurrency`: `group: "pages"`, `cancel-in-progress: false`.
- `build` job: checkout, `actions/configure-pages@v6`, build static site, `actions/upload-pages-artifact@v5`.
- `deploy` job: `needs: build`, `environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }`, `actions/deploy-pages@v5`.
