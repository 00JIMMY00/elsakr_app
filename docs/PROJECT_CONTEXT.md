# Project context

## Purpose and scope

`elsakr_app` is the Frappe app for Elsakr-specific changes. The repository also defines the app list and Docker deployment for the single production site, `elsakr.arab-erp.com`. The app includes a standard public `Operations` Workspace in the Elsakr App module, with Arabic sections for customers, suppliers, accounts, and stock. Its 21 shortcuts open existing ERPNext records and reports under the user's existing permissions. `hooks.py` requires ERPNext, installs the Item size Link field after installation/migration, overrides the Report controller for size filtering in Stock Balance/Stock Ledger, and extends those reports' scripts through the `get_script` endpoint override. `patches.txt` includes a pre-model-sync patch to rename the original `Operation` Workspace, whose route conflicts with ERPNext's manufacturing Operation DocType. Standard Workspace JSON is synced on app installation and migration.

The app also includes a public `Operations Dashboard` child Workspace under Operations. Two app-managed Custom HTML Blocks show company/date filters, four summary amounts, and charts for daily income/expenses and the ten best-selling Items. A read-only API uses submitted Sales Invoice Items and non-cancelled GL Entries, scoped to a permitted company. The default range is the first of the current month through today; receivables/payables are balances as of the end date. The blocks are installed after app install/migration and the standard Workspace JSON is synced with the app.

The app also defines the `Item Size` master (Arabic label «المقاس») with one
required, unique `size` field, and the optional Item Link `custom_size`. Stock
Balance and Stock Ledger display a size Link column after Item Name and accept the same optional Link filter. The column uses the current Item size and is also included in the server report output for export. Report execution
intersects the selected size with item/group/brand choices before calling the
native ERPNext calculation; no match returns empty rows. Reports without a size
filter retain the native execution path. Size filtering uses the Item's current
classification, including for historical stock movements.

Transaction child rows also carry read-only `custom_size`, fetched from the
selected Item and synchronized on server validation. Coverage includes sales
and purchase quotations/orders/invoices, Delivery Note, Purchase Receipt,
Material Request, Stock Entry, Stock Reconciliation, Pick List, and Packed Item
rows on supported parents. Existing submitted transactions are not backfilled.
The explicit `elsakr_app.demo.create_tyre_demo` helper is restricted to the
second development site and never runs from installation or migration.

Item variants synchronize `custom_size` from `Item Size`, `Size`, or `المقاس` attributes on validation. A variant with only one attribute uses that value even if the attribute has another name. Multi-attribute variants require one recognized size attribute for automatic size selection. Variant display names use the template name followed by all full attribute values; Item codes remain unchanged. Matching Item Size master
records are created automatically from nonempty attribute values when missing, using normal Item Size create permissions within the Item save transaction; existing records are reused. Templates carry no single size. Regular Items remain
unchanged. `elsakr_app.variant_demo.create_variant_demo` is an explicit,
development-only retained example and is never invoked by migration.

New Sales Invoices default `is_pos` to 1 through an installation/migration
Property Setter. Existing saved values are preserved. The form initializes its
Items grid to Item (2), المقاس (1), Quantity (1), Rate (2), Amount (2), replacing
older in-memory grid preferences for that form session. A selected customer has
an open-record icon during entry and a clickable Customer Name in read-only
mode, routed by the actual Customer ID.

Sales Invoice uses an app controller subclass to populate enabled company Cash/Bank
payment methods when Include Payment (POS) has no applicable POS Profile. Existing
profiles retain native ERPNext behavior. A DocType script corrects the section collapse dependency and opens the native
payment table in Details, below the customer header, when POS is selected. The
table is capped at 760 px and fits narrower screens. Payment allocation and ledger posting
remain native. The explicit `elsakr_app.payment_demo.create_payment_demo` helper
is restricted to the second development site and retains synthetic accounting
examples without stock movements; migration never invokes it.

The app also reapplies 15 selected Sales Invoice Hidden settings after install
and migration, keeping database DocFields used by Edit DocType aligned with
Property Setters used by Customize Form. Ten selected fields/sections/tabs are
hidden and five remain visible. The snapshot lives in
`elsakr_app/sales_invoice_visibility.py`; ERPNext source is not edited.

Sales Invoice also supports inline Customer Name autocomplete, optional Phone, and optional
Address. Existing customers can be found by name/ID or linked Contact phone; selection
loads their details. The controller resolves new Individual customers and linked native
Contact/Address records during `before_validate`, with normal permissions and rollback
inside the invoice save transaction. Exact unambiguous names are reused. Freeform
invoice addresses may omit City through a scoped hidden Address flag; ordinary addresses
retain the City requirement through client metadata and a validation hook. Country uses
the company/site default. The native Customer Link, party defaults, and accounting remain
in use. `customer_setup.py` installs these fields, captures the development Customer
Hidden settings and Individual default, and `public/js/customer.js` moves primary
address/contact details into Details while hiding the old tab.

Quick Entry is disabled for Item, Customer, Supplier, Sales Invoice, Material
Request, and Mode of Payment through app-managed DocType Property Setters after
install/migration. The app's own Item Size DocType also has Quick Entry disabled.
The normal New action for these records opens the full form directly.

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
