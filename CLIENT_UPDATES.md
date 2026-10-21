# Elsakr client updates

The only site is `elsakr.arab-erp.com`. Its production stack runs in Docker on
`ssh hassan`; Cloudflare Tunnel points to `127.0.0.1:8000`.

1. Push a commit to `elsakr_app/main` to release the app and refresh all
   installed apps from the branches in `apps.yaml`.
2. Every commit builds a new image on GitHub with the latest commits from the
   branches in `apps.yaml`, publishes it to GHCR, and deploys it on the client
   server. This includes README-only commits when you want to refresh
   upstream apps. The `elsakr-deploy` self hosted runner must be online.
3. For another app, add its `name`, public GitHub `repo`, and `ref` to
   [apps.yaml](apps.yaml). Keep `elsakr_app` in the list. The next build fetches
   the latest commit of each `ref` and deployment installs missing apps.
   A push to an upstream app alone does not start this workflow: push to
   `elsakr_app/main` or run the workflow manually to take that update.
4. Check the GitHub Actions result and `https://elsakr.arab-erp.com`.
   A failed update restores the previous image and the database/file backup.
   The first install has no prior release to restore.
   Backups remain in the site's `private/deploy-backups/deploy-*` directory.

## One-time setup

On the client machine, run `bash deploy/bootstrap.sh` from this repository.
GitHub requires a one-hour runner registration token from **Settings → Actions
→ Runners → New self-hosted runner**. Write that token to
`/home/hassan/elsakr-runner/registration-token` (mode `660`, group `docker`),
then run `docker compose -f /home/hassan/elsakr/runner.compose.yaml up -d`.
The runner removes the token file after registration. The generated ERPNext
Administrator password is stored in `/home/hassan/elsakr/.env` on that machine.

No custom GitHub Actions secrets are needed. GitHub's built-in `GITHUB_TOKEN`
publishes and pulls the image. Since this repo is public,
review pull requests before running them: a self hosted runner with Docker
access can execute code on the client machine.
