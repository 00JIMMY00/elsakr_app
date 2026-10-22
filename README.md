# Elsakr App

This is the Frappe app for changes specific to the Elsakr client. The single
production site is `elsakr.arab-erp.com`.

The local Bench also hosts `elsakr-dev2.arab-erp.com` with ERPNext and this app.
Its public hostname routes through this machine's Cloudflare Tunnel; see
[CLIENT_UPDATES.md](CLIENT_UPDATES.md).

The installed apps are declared in [apps.yaml](apps.yaml). See
[CLIENT_UPDATES.md](CLIENT_UPDATES.md) for the short update and deployment guide.
For ongoing work, see [project context](docs/PROJECT_CONTEXT.md),
[decisions](docs/DECISIONS.md), and [progress](docs/PROGRESS.md).

Production deployments run from `main` through GitHub Actions. CI installs the
apps and builds assets, then publishes a Docker image. The client machine pulls
that image and updates its containerized Frappe stack. A failed rollout restores
the previous image and the pre-migration database and files backup.

