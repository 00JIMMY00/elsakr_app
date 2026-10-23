# Progress

Add the newest update first. Each entry should state the change, the checks performed, and remaining work. Use **Local**, **Deployed**, or **Unverified** to make release status clear. Mark **Deployed** only after checking the production workflow and live site.

## 2026-10-23 — Open common DocTypes in full forms (Local)

- Changed: Disabled Quick Entry for Item, Customer, Supplier, Sales Invoice, Material Request, Mode of Payment, and Item Size. Added an installation/migration hook for the six ERPNext DocTypes and changed the app-owned Item Size metadata. Applied the change to `elsakr-dev2.arab-erp.com` through local migration.
- Checked: Local migration and a repeated setup call completed successfully. The site has six `quick_entry=0` DocType Property Setters and Item Size has `quick_entry=0` in its DocType record. Ruff lint/format, Python compilation, and `git diff --check` passed.
- Remaining: Browser confirmation is pending; reload Desk metadata before testing New on these lists. No production deployment was performed.

## 2026-10-23 — Add Operations dashboard child Workspace (Local)

- Changed: Added `Operations Dashboard` under `Operations` with two app-managed HTML blocks, shared company/From/To controls, revenue and expense totals, customer receivables and supplier payables, a daily income/expense chart, and a top-ten sales quantity chart. The default dates are the first of the current month through today. The balances use all entries through the selected end date. Applied the blocks and Workspace to `elsakr-dev2.arab-erp.com`.
- Checked: Python compilation, JavaScript syntax, and `git diff --check` passed. The local API returned figures and eight selling Items for 2026-10-01 through 2026-10-23, and empty activity/sales for 2026-09-01 through 2026-09-30. Confirmed the Workspace is a child of Operations, both public blocks exist, the Desk page API returns both blocks, the sidebar lists the new Workspace, and the dashboard JavaScript asset returns HTTP 200. Reapplying the block setup succeeded.
- Remaining: Visual browser review could not be completed because the saved development Administrator credential was rejected by the login endpoint; no password was changed. No production deployment was performed.

## 2026-10-23 — Match Edit DocType to Customize Form Hidden flags (Local)

- Changed: Added an explicit 15-field Sales Invoice visibility snapshot: ten hidden and five visible, matching the second development site's existing Hidden Property Setters. Installation/migration now updates both the database DocFields and corresponding Property Setters, preserving other customization properties and avoiding ERPNext source exports. Applied it twice on `elsakr-dev2.arab-erp.com`.
- Checked: Compared all 15 raw DocField flags, effective metadata flags, and Hidden Property Setters; all match with no duplicate setters. Temporarily reset one database flag to mimic upstream metadata sync, verified setup restored it, and rolled back the simulation. Headless Chrome opened Edit DocType and confirmed the requested field flags. Rechecked POS payments in Details, 760 px desktop / 303 px mobile layout, toggle off/on, 400/600 allocation with EGP 1,000 paid and zero outstanding, and the retained submitted invoice. Ruff lint/format, Python compilation, and `git diff --check` passed.
- Remaining: No production deployment was performed. Reload Desk to load the updated metadata. Future permanent changes to these Hidden flags must update the app snapshot because migration reapplies it.

## 2026-10-23 — Move POS payments into Details with a narrower table (Local)

- Changed: Moved the existing Sales Invoice payment section into Details, immediately below the customer/invoice header. Updated its field-to-tab references so navigation and validation target Details. Limited the native grid to 760 px, with full available width on smaller screens; refreshes reuse the same grid.
- Checked: Headless Chrome on the development HTTPS site verified Details is the actual parent tab, exactly one payment grid exists, desktop width is 760 px, and a 390 px mobile viewport fits the grid at 303 px. Native field events still calculate a 400/600 split as EGP 1,000 paid and zero outstanding. Turning POS off hides the section; turning it back on and refreshing restores its two methods in Details. Submitted invoice `ACC-SINV-2026-00004` also shows its payment grid in Details with EGP 1,000 paid and zero outstanding. JavaScript syntax and `git diff --check` passed.
- Remaining: No production deployment was performed. Reload Desk on `elsakr-dev2.arab-erp.com` to load the layout change.

## 2026-10-23 — Show POS payment methods and verify split-payment accounting (Local)

- Changed: Added a Sales Invoice form script to expand the native payment section and open its tab on Include Payment (POS). Corrected the collapse dependency in client metadata: Frappe expands on a true dependency, so the upstream `eval:!doc.is_pos` kept collapsing the POS table. Added a Sales Invoice controller subclass that loads enabled company methods mapped to enabled leaf Cash/Bank accounts when no POS Profile applies; existing profile behavior and all accounting remain native. Added an explicit development-only retained payment demo helper.
- Development setup/data: Corrected Credit Card's company mapping from Debtors to newly created `DEMO POS Bank - T` on `elsakr-dev2.arab-erp.com`. Retained submitted invoices `ACC-SINV-2026-00003` (EGP 1,000 Cash) and `ACC-SINV-2026-00004` (EGP 400 Cash + EGP 600 Credit Card), dated 2026-10-23. Both have zero outstanding and no stock movements; earlier inventory demo balances remain unchanged.
- Checked: Verified persisted GL rows for both invoices: EGP 1,000 sales credit and EGP 1,000 customer debit, with payment credits clearing the customer against Cash/Bank debits. Total debits equal credits and net customer balance is zero for each invoice. Verified no-profile loading, repeated loading without duplicate methods or loss of entered amounts, and POS-disabled behavior. A headless Chrome session over the development HTTPS site verified that selecting POS opens Payments with the Cash/Card table visible, then exercised the native item/payment field events for a 400/600 split: total and paid EGP 1,000, outstanding zero, table still visible. Ruff lint/format, Python compilation, JavaScript syntax and `git diff --check` passed.
- Remaining: Production deployment has not been performed. Reload Desk on the development site to load the script. Production operators must configure correct company Cash/Bank mappings and profile methods; the development setup/demo helper never runs on migration.

## 2026-10-23 — Fix single-attribute size creation and full variant names (Local)

- Changed: Extended variant size detection to `Size`/`المقاس` aliases and single-attribute fallback. Variant display names now contain the template name and full attribute values instead of abbreviations; Item codes are preserved. Repaired the user-reported existing single Colour/White variant on `elsakr-dev2.arab-erp.com`, creating/reusing White and selecting it as size.
- Checked: Confirmed the reported saved Item contains the White size Link, full White display-name suffix, and unchanged code. Used native variant creation with a temporary full Colour value to verify automatic size creation and reuse on repeated save. Verified canonical size behavior, Size alias selection, and full multi-attribute display names. Rolled back temporary fixtures while retaining the reported Item repair. Ruff lint/format and `git diff --check` passed.
- Remaining: Browser confirmation is pending; reload the reported Item. Other existing variants update when saved. No production deployment was performed.

## 2026-10-23 — Auto-create size masters from variant attribute values (Local)

- Changed: Updated Item validation so saving a variant based on the `Item Size` attribute creates a missing size master from the selected attribute value and assigns `custom_size`. Existing sizes are reused; empty values are rejected. Creation uses normal permissions, duplicate-tolerant insertion, and the same transaction as the Item save.
- Checked: On `elsakr-dev2.arab-erp.com`, added a temporary new attribute value and used ERPNext's native `create_variant` plus Item insert to verify automatic master creation and persisted Item linkage. Repeated save kept exactly one master. Saving an existing variant with a cleared Link restored its existing size. Verified the template still has no single size, then rolled back all temporary fixtures and confirmed both new master and variant disappeared together. Existing retained demo data remains. Ruff lint/format and `git diff --check` passed.
- Remaining: Visual browser review is pending; reload Desk and create a variant using the size attribute. No production deployment was performed.

## 2026-10-23 — Retain a native tyre variant example (Local)

- Changed: Added Item validation to derive `custom_size` from canonical `Item Size` variant attributes. Created template `DEMO-TYRE-MODEL-X` with three variants in `DEMO Tyre Variants` on `elsakr-dev2.arab-erp.com`. Retained submitted purchase invoice `ACC-PINV-2026-00002` and sales invoice `ACC-SINV-2026-00002`, dated 2026-10-23, with stock updates. Earlier demo data remains in place.
- Checked: Creation corrected deliberately mismatched size Links for all three variants. Verified transaction row sizes, six size-filtered Stock Balance/Stock Ledger runs scoped to the new group, and Bin quantities of 18 (185/65 R14), 27 (195/65 R15), and 36 (205/55 R16). Verified three persisted variants, no stock ledger rows for the template, resave synchronization, missing size master rejection, and ordinary Item behavior. Rolled back only the additional validation checks; demo invoices/items remain committed. Ruff lint/format and `git diff --check` passed.
- Remaining: Visual browser review is pending. Open the template or retained sales invoice to try the model/size workflow. No production deployment was performed.

## 2026-10-23 — Display size in stock report columns (Local)

- Changed: Added a «المقاس» Link column after Item Name in Stock Balance and Stock Ledger, populated from current Item sizes in a single batch lookup. The column is present with or without the size filter and on empty results; non-item summary rows remain blank. Native report quantities and totals are retained.
- Checked: On `elsakr-dev2.arab-erp.com`, verified all four retained demo sizes in both reports, selected-size results, empty results, exactly one size column, and unchanged aggregate stock of 86 units. Authenticated HTTPS report runs returned the column and correct values for 175/70 R13 in both reports. Ruff lint/format and `git diff --check` passed. Demo data was retained.
- Remaining: Visual browser review is pending; refresh reports to show the column. No production deployment was performed.

## 2026-10-23 — Show transaction sizes and retain tyre demo data (Local)

- Changed: Added read-only fetched size columns to Quotation Item, Sales Order Item, Delivery Note Item, Sales Invoice Item, Supplier Quotation Item, Purchase Order Item, Purchase Receipt Item, Purchase Invoice Item, Material Request Item, Stock Entry Detail, Stock Reconciliation Item, Pick List Item, and Packed Item. Added server validation on the 12 parent transaction types. Applied fields to `elsakr-dev2.arab-erp.com`. Added an explicitly invoked development-only tyre demo helper.
- Retained demo data: Created four `DEMO-TYRE-*` Items (175/70 R13, 185/65 R14, 195/65 R15, 205/55 R16), a demo item group, synthetic customer/supplier, and Main/Branch demo warehouses. Submitted purchase invoice `ACC-PINV-2026-00001`, sales invoice `ACC-SINV-2026-00001`, stock entries `MAT-STE-2026-00001` through `MAT-STE-2026-00003` (receipt, transfer, issue), and reconciliation `MAT-RECO-2026-00001`, all dated 2026-10-23. These are intentional test records, not private customer data.
- Checked: Verified all 13 field definitions, size values on all six submitted documents, server synchronization/change/clear behavior across all 12 parent types, and eight size-filtered native report runs (both reports for each size). Stock Balance totals matched Bin quantities: 20, 21, 29, 16 respectively. Committed the records for manual testing; no demo records were removed. Authenticated HTTPS checks verified submitted purchase/sales invoice, stock transfer, and reconciliation rows contain sizes; both stock reports returned only the selected demo size and Stock Balance matched 20 units for 175/70 R13. Ruff lint/format, Python compilation, and `git diff --check` passed.
- Remaining: Visual browser review is pending. Reload Desk to refresh child-table metadata; filter reports to 2026-10-23 and the demo warehouses/Item group. No production deployment was performed.

## 2026-10-23 — Add Item size master and stock report filters (Local)

- Changed: Added standard `Item Size` («المقاس») with one required unique field, optional Item Link `custom_size` labelled «المقاس», and installation/migration setup. Extended the existing Stock Balance and Stock Ledger scripts with a size Link filter and scoped report execution to matching items before native calculations. Applied the schema and field setup to `elsakr-dev2.arab-erp.com`; repeated setup succeeded.
- Checked: Ran both reports through Frappe's report `run` endpoint function using three temporary items (two different sizes and one unclassified), three sizes (one unused), and six submitted stock receipts across opening/current periods. Verified unfiltered results, matching size, opening and closing quantities, unused size returning empty, conflicting item selection returning empty, item-list intersection, and item-group selection. Rolled back fixtures and verified zero test Items, sizes, or Stock Ledger Entries remained. Executed the actual report JavaScript in Node: the Link filter appears once and native filters/formatter/onload remain. Authenticated HTTPS `get_script` responses include the filter for both reports; the HTTPS master schema contains one field, and Arabic translation resolves to «المقاس». Python compile, JavaScript syntax, and `git diff --check` passed.
- Remaining: Visual browser review is pending; reload Desk to load the new report scripts and Item metadata. No production deployment was performed.

## 2026-10-23 — Fix Workspace save name conflict (Local)

- Changed: Renamed the standard app Workspace from `Operation` to `Operations` and moved its JSON to `workspace/operations/operations.json`. Added a pre-model-sync patch that renames the older app-owned Workspace while preserving its layout and shortcuts. Applied the rename to `elsakr-dev2.arab-erp.com` and cleared cache. Updated user-facing instructions to `/app/operations`.
- Checked: Reproduced the original error through Frappe's Desk `save_page` method and confirmed the conflicting ERPNext `Operation` DocType. After the patch, verified an actual heading edit through `save_page` and a metadata save through `update_page` both succeed, then rolled back the test edit. Verified the original layout and all 21 shortcuts survived the rename, the patch can be called twice, and Operations appears in the sidebar and Workspace API. No ERPNext Operation records were changed.
- Remaining: Browser confirmation is pending; users should reload Desk and open the new route. No production deployment was performed.

## 2026-10-23 — Add Operation Workspace (Local)

- Changed: Added a standard public `Operation` Workspace in the Elsakr App module with four Arabic sections and 21 shortcuts: customers and receivables summaries, suppliers and payables summaries, accounts/invoices/Trial Balance/Gross Profit, and stock reports/entries/warehouses/items/groups/reconciliation. Applied the Workspace JSON to `elsakr-dev2.arab-erp.com` and cleared the site's cache. Existing Workspaces are retained.
- Checked: All 21 targets exist in the site's database; all eight reports are enabled Script Reports; all five Tree shortcuts point to tree DocTypes. Frappe's Workspace sidebar includes Operation for Administrator, and `get_desktop_page` returns all 21 shortcuts with query-report routing for all eight reports. The saved layout contains four section headers. `git diff --check` passed. External HTTPS `/app/operation` responds and redirects unauthenticated access to login.
- Remaining: Visual browser review and authenticated HTTPS verification were not completed: the local saved Administrator credential was rejected by the HTTPS login endpoint. No password was changed. No production release was triggered; the normal production migration will sync this Workspace when released.

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
