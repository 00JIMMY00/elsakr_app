# Elsakr App

This is the Frappe app for changes specific to the Elsakr client. The single
production site is `elsakr.arab-erp.com`.

The installed apps are declared in [apps.yml](apps.yml). See
[CLIENT_UPDATES.md](CLIENT_UPDATES.md) for the short update and deployment guide.

Production deployments run from `main` through GitHub Actions. CI installs the
apps and builds assets, then publishes a Docker image. The client machine pulls
that image and updates its containerized Frappe stack. A failed rollout restores
the previous image and the pre-migration database and files backup.

