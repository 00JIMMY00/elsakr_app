# Decisions

Record lasting choices here. Add a new dated entry when a choice changes; keep the earlier entry for history.

## 2026-10-23 — Host the second Elsakr development site in the local Bench

**Decision:** Keep `elsakr-dev2.arab-erp.com` as a separate site in the existing DNS multitenant Bench, with ERPNext and `elsakr_app`. Route its public hostname to that Bench through the existing Cloudflare Tunnel when the Cloudflare configuration is added.

**Reason:** The requested second development site needs its own database and site directory without changing the Docker production deployment or the original development site.

**Consequence:** App changes in this Bench affect both development sites at the code level, while each site has separate data and installed-app state. Cloudflare hostname routing is an additional setup step; creating the Bench site alone does not publish it.

## 2026-10-23 — Keep project tracking in the repository

**Decision:** Use this file for lasting decisions, `PROJECT_CONTEXT.md` for current facts, and `PROGRESS.md` for dated work and verification. Keep the instructions in the root `AGENTS.md`.

**Reason:** Changes to code and deployment can be reviewed with the context that explains them. The files travel with the repository and can be updated in the same commit.

**Consequence:** Each meaningful change includes a progress entry; architecture or process changes update the relevant context and decision entries.

## Existing deployment choices (documented 2026-10-23)

These choices were already implemented before the tracking files were added; their original decision dates are not recorded here.

- **One production site:** `elsakr.arab-erp.com` is the only site described in the repository. This keeps deployment and health checks specific to that site.
- **Image-based releases:** A push to `main` builds an image with the latest configured app refs and deploys it through the self-hosted runner. An upstream app push alone does not trigger this workflow.
- **Back up before migration:** The rollout stores a database and files backup outside Frappe's normal backup cleanup path and attempts restoration if deployment fails. The initial install has no previous release for rollback.
