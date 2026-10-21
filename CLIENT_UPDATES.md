# Elsakr client updates

The only site is `elsakr.arab-erp.com`. Its production stack runs in Docker on
`ssh hassan`; Cloudflare Tunnel points to `127.0.0.1:8000`.

1. Develop on `develop` and open a pull request. CI installs ERPNext, the theme,
   and `elsakr_app`, builds assets, and runs app tests if present.
2. Merge into `main`. The same workflow builds an image, publishes it to GHCR,
   and deploys it on the client server. The deploy job requires the
   `elsakr-deploy` self hosted runner to be online.
3. For another app, add its `name`, public GitHub `url`, and `ref` to
   [apps.yml](apps.yml) before `elsakr_app`. Update its `ref` to release an
   upstream change. CI builds all listed apps; deployment installs missing apps.
4. Check the GitHub Actions result and `https://elsakr.arab-erp.com`.
   A failed rollout restores the previous image and the database/file backup.
   Backups remain in the site's `private/backups/deploy-*` directory.

## One-time setup

On the client machine, run `bash deploy/bootstrap.sh` from this repository.
GitHub requires a one-hour runner registration token from **Settings → Actions
→ Runners → New self-hosted runner**. Write that token to
`/home/hassan/elsakr-runner/registration-token` (mode `660`, group `docker`),
then run `docker compose -f /home/hassan/elsakr/runner.compose.yaml up -d`.
The runner removes the token file after registration. The generated ERPNext
Administrator password is stored in `/home/hassan/elsakr/.env` on that machine.

No custom GitHub Actions secrets are needed. The workflow uses GitHub's built-in
`GITHUB_TOKEN` to publish and pull the image. Keep **Actions → General →
Workflow permissions** set to allow package writes. Since this repo is public,
review pull requests before running them: a self hosted runner with Docker
access can execute code on the client machine.
