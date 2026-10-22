# Project context

## Purpose and scope

`elsakr_app` is the Frappe app for Elsakr-specific changes. The repository also defines the app list and Docker deployment for the single production site, `elsakr.arab-erp.com`. The app package currently contains Frappe scaffolding; `hooks.py` has no active customization hooks and `patches.txt` lists no patches.

## Source of truth

- `elsakr_app/`: Python app, hooks, modules, and patches.
- `apps.yaml`: installed apps, repository branches, and Frappe branch. Currently Frappe v15, ERPNext `version-15`, `arab_erp_theme` `develop`, and this app at the workflow commit.
- `.github/workflows/ci.yml`: builds and publishes an image on every push to `main` or manual dispatch, then deploys it through the client machine's self-hosted runner.
- `.github/workflows/linter.yml`: pull request pre-commit and Semgrep checks, plus a dependency audit.
- `deploy/`: Docker image, Compose stack, server bootstrap, and rollout script.
- `CLIENT_UPDATES.md`: operator instructions for updates and first-time setup.

## Deployment flow

The build fetches the latest commits from the refs in `apps.yaml`, packages the apps into a GHCR image, and passes its digest to the deployment job. The client machine runs the Docker stack; its frontend listens on `127.0.0.1:8000` behind Cloudflare Tunnel. The rollout script pulls the image, backs up the existing site, installs any newly listed apps, migrates, syncs assets, and checks the site. On a failed update, it attempts to restore the previous image and site backup. A first install has no previous release to restore.

The repository documents the deployment mechanism; it does not itself prove the current production image or site health. Confirm those in GitHub Actions and on the live site before recording a release as deployed.

## Local work

The app is in a Bench workspace. The local Bench contains `elsakr-dev.arab-erp.com` and `elsakr-dev2.arab-erp.com`; the latter was created with Frappe, ERPNext, and `elsakr_app` on 2026-10-23. The Bench uses DNS multitenancy on port 8000, so requests to the new site require its hostname in the Host header. Its scheduler is disabled, matching the existing Elsakr development site. The production Docker deployment is separate and does not create or update this local site. Run focused checks for changed code or configuration. Follow `AGENTS.md` when updating the tracking files.

The local machine's Cloudflare Tunnel forwards development hostnames, including `elsakr-dev2.arab-erp.com`, to the Bench on `http://localhost:8000`. Cloudflare's authoritative DNS resolves the new hostname, and its external HTTPS route returned HTTP 200 on 2026-10-23.
