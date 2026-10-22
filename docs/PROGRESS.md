# Progress

Add the newest update first. Each entry should state the change, the checks performed, and remaining work. Use **Local**, **Deployed**, or **Unverified** to make release status clear. Mark **Deployed** only after checking the production workflow and live site.

## 2026-10-23 — Restore access to second development site (Local)

- Changed: Set the local machine's active `eno1` DNS resolver to `1.1.1.1` and `1.0.0.1`, then flushed its DNS cache. This is a runtime resolver setting and may be replaced by a network reconnection.
- Checked: Both Cloudflare authoritative nameservers and `1.1.1.1` resolved `elsakr-dev2.arab-erp.com`. The router DNS (`192.168.1.1`) and `8.8.8.8` still returned cached `NXDOMAIN`. After the local resolver change, the normal external HTTPS URL returned HTTP 200 and `/api/method/ping` returned `{"message":"pong"}`. The site's local Bench endpoint also returned HTTP 200.
- Remaining: Browsers using their own cached DNS or a different resolver may need a restart or cache expiry. No production workflow deployment was performed.

## 2026-10-23 — Create second Elsakr development site (Local)

- Changed: Created `elsakr-dev2.arab-erp.com` in the local Bench with Frappe, ERPNext, and `elsakr_app`; set its public `host_name`. Its Administrator password was saved in a local file with mode `600`.
- Checked: `bench --site elsakr-dev2.arab-erp.com list-apps` lists all three apps. Requests with the site's Host header to `127.0.0.1:8000` returned HTTP 200 for `/` and `/api/method/ping` (`{"message":"pong"}`). Administrator login returned HTTP 200 with `Logged In`. `bench doctor` reported one worker online and the scheduler disabled, as on the original development site.
- Remaining at that check: Cloudflare's authoritative DNS returned `NXDOMAIN` for the new hostname. The route and external HTTPS URL were verified later on 2026-10-23. No production deployment was performed.

## 2026-10-23 — Start project tracking (Local)

- Added repository instructions and the project context, decisions, and progress files.
- Reviewed the app structure, app list, GitHub workflows, and rollout configuration to establish the baseline.
- Production deployment and current site health were not checked. No app runtime behavior was changed.

## Entry template

Copy this block for future work and remove any fields that do not apply:

```markdown
## YYYY-MM-DD — Short change summary (Local | Deployed | Unverified)

- Changed: ...
- Checked: ...
- Remaining: ...
```
