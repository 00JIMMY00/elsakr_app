# Progress

## 2026-10-25 — Restore missing dashboard Workspace source (Local + production repair)

- Cause: Production had both dashboard HTML blocks and the JavaScript asset, but `Workspace/Operations Dashboard` returned HTTP 404. The latest workflow for commit `56eba0589434949f63c05176f7b0e04d23b95f73` completed both image and deploy jobs successfully. The Workspace existed in the development database but its standard JSON was absent from Git; the block setup hook does not create Workspaces.
- Changed: Exported the standalone public Workspace to `elsakr_app/elsakr_app/workspace/operations_dashboard/operations_dashboard.json`, including both block references and the layout. Added a regression check that deletes the database Workspace inside a rolled-back transaction, imports the source through Frappe's standard importer, reapplies block setup twice, and checks Desk/sidebar availability. Corrected the setup module description.
- Checked locally: Regression check passed; full migration on `elsakr-dev2.arab-erp.com` completed. Ruff lint/format, Python compilation, JSON validation, and diff whitespace checks passed.
- Production repair: Created only the missing Workspace through the authenticated native resource API using the same source JSON. Verified persisted layout/properties/block references, both blocks in the Desk page API, sidebar visibility, dashboard API HTTP 200, and route HTTP 200. An authenticated headless Chrome visit rendered exactly one summary and one charts block, loaded dashboard data with HTTP 200, and reported no page JavaScript errors. No financial records were changed.
- Remaining: Commit and push the source changes so future images include the Workspace. This was a verified live metadata repair, not a new image deployment. The repository fix has not yet run through the production workflow.

## 2026-10-25 — Default Operations Dashboard to Today (Local)

- Changed: Set the initial date range and selected preset to Today, including the stored summary block's initial button state and the API's omitted-date defaults. Kept explicit presets/custom dates and session selections. Refreshed dashboard blocks/cache on `elsakr-dev2.arab-erp.com`; updated README, operator instructions, context, and decisions.
- Checked: Development HTTPS Chrome confirmed Today selected, both dates set to today, and successful initial data loading. A no-argument API call returned today's start/end dates. Switching to Month and back to Today worked without page errors or writes. JavaScript syntax, ESLint, Python compilation, Ruff lint, and diff whitespace checks passed.
- Remaining: Reload Desk for the new initial range. No production deployment was performed.

## 2026-10-25 — Remove informal Operations captions (Local)

- Changed: Removed all descriptive captions beneath the four quick actions and six card headings, including the informal expense caption. Removed unused subtitle data and CSS, retained concise action/group labels, and changed loading/error messages to formal Arabic. Refreshed the managed block/cache on `elsakr-dev2.arab-erp.com`; aligned README, operator instructions, and current context.
- Checked: Development HTTPS Chrome confirmed no action captions or card descriptions, six cards, 25 links, four actions, and the Sales Invoice list route. Layout fit at 1440/390/320 px with no JavaScript page errors or saved records. JavaScript syntax, ESLint, Prettier, and diff whitespace checks passed.
- Remaining: Reload Desk for the updated script and block. No production deployment was performed.

## 2026-10-25 — Remove Operations footer slogan (Local)

- Changed: Removed the footer slogan and divider lines, deleted their unused CSS, and refreshed the managed block/cache on `elsakr-dev2.arab-erp.com`. Updated README and operator instructions.
- Checked: Read back the stored Custom HTML Block and confirmed it ends after the navigation section with no footer. Prettier and diff whitespace checks passed.
- Remaining: Reload the workspace to load the updated block. No production deployment was performed.

## 2026-10-25 — Enlarge Operations text and reduce card spacing (Local)

- Changed: Increased tool/quick-action labels from 12 px to 16 px and group titles from 14 px to 18 px, with larger supporting text and report badges. Reduced card header/action padding, navigation insets, corner radii, icon containers, and gaps. Trimmed Frappe's widget/content padding only around the Operations block instance. Refreshed the managed block and cleared cache on `elsakr-dev2.arab-erp.com`; updated README, operator instructions, and current context.
- Checked: Development HTTPS Chrome confirmed 16 px labels and 18 px headings, six cards, 25 links, four actions, and no reintroduced banner/search/filter controls. Verified no horizontal overflow in the block or action/card/link containers at 1440/768/390/320 px and reviewed the desktop screenshot. No JavaScript page errors or saved business records. JavaScript syntax, ESLint, Prettier, and diff whitespace checks passed.
- Remaining: Reload Desk for the updated block CSS and JavaScript. No production deployment was performed.

## 2026-10-25 — Simplify Operations to quick actions and cards (Local)

- Changed: Removed the introductory banner/illustration, both section headings and their captions, search box, and category filter buttons at the user's request. Removed their unused JavaScript handlers and CSS. Retained the four permission-aware quick actions, six navigation cards, and native shortcut routing/access/loading/error/retry handling. Updated README, operator instructions, current context, and the design decision. Refreshed the managed block and cleared cache on `elsakr-dev2.arab-erp.com`.
- Checked: Development HTTPS Chrome confirmed six cards, all 25 links, four actions, and absence of the removed sections. Verified the Sales Invoice list link, visible quick actions, and no horizontal overflow at 1440/390/320 px. The browser reported no JavaScript page errors and saved no records. JavaScript syntax, ESLint, Prettier, and diff whitespace checks passed.
- Remaining: Reload Desk to load the refreshed block and JavaScript. No production deployment was performed.

## 2026-10-25 — Redesign Operations as an automotive shop hub (Local)

- Changed: Replaced the flat Operations shortcut layout with an app-managed Custom HTML Block: Arabic RTL charcoal/amber header, original inline tire/oil/battery illustration, four permission-aware creation actions, Arabic/English search, category filters, and six colored navigation cards. Retained all 25 existing shortcut definitions and their native views, using Frappe's permission-filtered Workspace endpoint and route generator. Added responsive/dark-theme styling, keyboard focus, and loading/empty/error/retry states. Added install/migrate setup and updated the architecture, decision, README, and operator documentation. Applied the block and Workspace to `elsakr-dev2.arab-erp.com` and cleared cache.
- Checked: Development HTTPS Chrome checks rendered six cards, 25 links, and four creation actions; Arabic/English search, no-result reset, and category filtering passed. Verified no horizontal overflow at 320/390/768/1440 px and reviewed desktop, phone, and dark-theme screenshots. Actual navigation opened native Stock Balance, Item Group tree, and new Sales Invoice, Purchase Invoice, Expense Entry, and Stock Entry forms. Simulated restricted/read-only responses hid unavailable links and creation actions; empty access, request failure, and retry recovery passed. A temporary Sales User received a proper subset of native shortcuts and could read the public block; its fixture was rolled back and absence confirmed. Repeated block setup retained all 25 destinations/views. Browser checks saved no business records and reported no JavaScript page errors. JavaScript syntax, ESLint, Prettier, Python compilation, Ruff lint/new-module formatting, JSON consistency, and diff whitespace checks passed.
- Remaining: Reload Desk and open `/app/operations` on the second development site. Production deployment has not been performed; the normal release must sync the Workspace, managed block, and JavaScript asset.

## 2026-10-25 — Require positive Selling Price and remove its caption (Local)

- Changed: Made Selling Price conditionally mandatory for saleable Items and variants and enforced a finite value greater than zero on the server for both creation and later saves, including unchanged empty/zero values. Templates and non-saleable Items remain exempt. Removed the explanatory caption from both new and saved forms, retaining list/currency/UOM context on saved Items. Applied metadata setup and cleared cache on `elsakr-dev2.arab-erp.com`; updated user/operator and project documentation.
- Checked: All 11 focused pricing tests passed, including blank/zero/negative rejection for new and saved Items, missing-price rejection on unchanged save, non-saleable exemption, template/variant creation, and existing pricing regressions. Test fixtures were rolled back. Development HTTPS browser checks confirmed the required marker and absence of the caption on a saved variant and a new Item; no browser records were created. Ruff lint/format, Python compilation, JavaScript syntax, and diff whitespace checks passed.
- Remaining: Reload Desk for the updated field metadata and script. Existing unpriced saleable Items need a positive price on their next save. No production deployment was performed.


## 2026-10-25 — Keep selling prices visible and editable on saved Items (Local)

- Changed: Exposed native Standard Selling Rate as Selling Price (سعر البيع) on saleable Items and saved variants, hiding it on templates. Added Item onload/validation/update hooks to display the current general stock-UOM Item Price and save explicit edits to the native price record within the Item transaction. Added price list/currency/UOM context, stale-edit checks, normal Item Price permissions, and guidance for multiple/quantity-specific prices. Installation/migration manages the field metadata; applied setup twice on `elsakr-dev2.arab-erp.com`. Updated user/operator and architecture documentation.
- Checked: Eight transaction-backed tests passed for saved-price updates and native invoice price lookup, external price changes/unrelated saves, stale edits, zero/negative values, missing-price creation, multiple active prices, saved variants, and permission denial. Test fixtures were rolled back. Development HTTPS browser checks confirmed the field's label and list/currency/unit context, an edit from 123 to 234 persisting after Save and reload, mobile visibility at 390 px, and visibility/current price on an existing saved tyre variant; no JavaScript errors were reported. Both temporary browser Items and their Item Prices were removed; retained demo records were not edited. Repeated setup, Ruff lint/format, Python compilation, JavaScript syntax, and diff whitespace checks passed.
- Remaining: Reload Desk to load updated scripts/metadata. Sales Invoice still uses native customer/POS price-list selection, dated prices, units, and pricing rules; existing invoices are not repriced. No production deployment was performed.


## 2026-10-25 — Keep new Sales Invoices at the header and fix customer-entry warning (Local)

- Changed: Removed the Sales Invoice POS handler's automatic scroll to Payments. Added a form-scoped guard for native Customer Address changes when both Customer and Customer Address are empty, clearing the address display without starting a party-dependent tax lookup. Existing customer/address handling remains native. Cleared cache on `elsakr-dev2.arab-erp.com` and updated user/operator instructions.
- Checked: Reproduced both issues in the development HTTPS browser before the fix, including the empty Customer Address handler's mandatory-party exception. After the fix, desktop browser checks confirmed a new POS invoice starts at scroll position zero, new and replacement customer names produce no warning, replacement clears linked details, existing customers load native receivable defaults and invoke native address tax handling, and POS toggling retains one visible payment grid without scrolling. A separate 390 px phone browser check confirmed scroll position zero on opening and no mandatory-party warning after entering a new name. JavaScript syntax, ESLint, and diff whitespace checks passed. Browser checks used unsaved invoices and did not create customer or invoice records.
- Remaining: Reload Desk to load the updated script. No production deployment was performed.

## 2026-10-25 — Open the dashboard from the site root and disable release popups (Local)

- Changed: Added installation/migration setup for a native Website Settings root redirect (HTTP 302 to `/app/operations-dashboard`) and enabled both native System Settings flags that disable update-available and change-log notifications. Setup updates an existing root redirect, removes duplicate root rules, and preserves other redirects. Applied to `elsakr-dev2.arab-erp.com`.
- Checked: Repeated setup twice successfully; confirmed exactly one root rule, both persisted flags and their Desk defaults, unchanged login routing, and no message from the disabled update-popup endpoint. External development HTTPS returned 302 from `/` to the dashboard; following redirects reached HTTP 200 at login with the dashboard as the return destination. Python compilation and diff whitespace checks passed. Ruff was unavailable in PATH and the Bench environment.
- Remaining: Reload existing Desk sessions to load notification preferences. Visual authenticated browser confirmation is pending. No production deployment was performed.

## 2026-10-23 — Simplify dashboard and make its Workspace independent (Local)

- Changed: Removed the introductory Arabic header and company selector, kept date filters, and made Operations Dashboard a standalone public Workspace with no parent. The existing API chooses the permitted default company automatically. Updated operator and project documentation. Applied blocks, reloaded the standard Workspace, and cleared cache on the second development site.
- Checked: JavaScript syntax and ESLint passed. Local Workspace metadata returned an empty parent and public=1. Development HTTPS browser checks passed for populated totals/rankings, 320/390/768 px fit, date presets, empty results, stale-response protection, simulated failures, and multi-date activity/table rendering.
- Remaining: Production deployment has not been performed. Reload Desk for the new sidebar placement and stored blocks.

## 2026-10-23 — Redesign Operations dashboard for phones (Local)

- Changed: Rebuilt the Arabic RTL dashboard with a navy/teal financial overview, revenue-minus-expenses result, four compact metric cards, separated currency labels, touch-sized Today/Last 7 Days/This Month presets, and expandable company/custom-date filters (initially collapsed on phones). Replaced numbered product columns and the separate key with named horizontal ranking bars. Added a responsive SVG activity chart, grouped bars for a single activity date, an expandable exact daily-values table, dark-theme styling, and explicit loading/empty/error states. Both blocks now share one request/result and ignore older responses. Existing API queries, permissions, currency, and balance/date semantics are retained. Applied the managed blocks and cleared cache on `elsakr-dev2.arab-erp.com`.
- Checked: Headless Chrome over development HTTPS verified four totals and eight retained demo sellers, rendered activity bars, quick-date changes, September empty states, rejection of a delayed older result, and clearing both blocks after a simulated request failure. A synthetic three-date response verified both line series, negative amounts, and three exact-values table rows without writing records. Checked desktop at 1440 px and dashboard fit at 320/390/768 px; a fresh 390 px load had collapsed filters and an expandable daily table. Reviewed desktop, phone, and dark-theme screenshots. The final browser run reported no JavaScript errors. JavaScript syntax, ESLint, and diff whitespace checks passed. Repeated block synchronization succeeded.
- Remaining: Reload Desk to load the refreshed blocks and JavaScript. Production deployment has not been performed; production requires the normal app update/migration to sync the stored HTML/CSS blocks.

## 2026-10-23 — Lock selected invoice party details and hide purchase tax fields (Local)

- Changed: Added native `read_only_depends_on` conditions to Sales Invoice and Purchase Invoice Phone/Address fields. Selecting an existing customer/supplier locks both fields; a new inline party leaves them editable. Added `apply_tds`, `taxes_and_charges_added`, `taxes_and_charges_deducted`, and `total_taxes_and_charges` to the app-managed Purchase Invoice Hidden snapshot. Applied both setup functions to `elsakr-dev2.arab-erp.com`.
- Checked: Both setup calls succeeded. Local effective metadata assertions confirmed all four read-only conditions and all four Hidden flags; database DocField Hidden flags also matched. Python compilation and diff whitespace checks passed. Ruff was unavailable on PATH.
- Remaining: Reload Desk to load metadata; visual browser verification is pending. No production deployment was performed.

## 2026-10-23 — Mirror the simplified sales flow in purchasing (Local)

- Changed: Added direct Supplier Phone entry with automatic native Contact creation/reuse, Individual defaults, hidden series/extra fields, and address/contact cards plus primary details in Details. Added Purchase Invoice Supplier Name autocomplete with name/ID/linked-phone search, optional Phone/Address, automatic linked master creation during save, and Supplier navigation links. Added the matching five-column Item/size/quantity/rate/amount grid, hidden series and extra sections/tabs, native Paid method/account/amount controls in Details, and an orange company-currency net-payable card. Retained the native unpaid default, purchase bill references, header withholding controls, permissions, accounting, and inherited validation. Existing sales/customer modules remain unchanged. Added install/migrate setup and purchasing regression tests. Applied setup and a full migration on `elsakr-dev2.arab-erp.com`.
- Checked: All 38 sales/purchasing transaction-backed tests passed. The 20 purchasing tests also passed after the final controller change, covering Supplier phone entry/change/reuse/shared contacts, inline creation and rollback, name-only entry, duplicate-name selection, name/phone search, permission denial, normal Address City requirements, payable balances, payments/settlement, supplier/company isolation, foreign currency, credit balances, draft/cancelled/future entries, and actual paid-invoice cash/payable GL posting. Headless Chrome over development HTTPS verified one-save Supplier/Contact creation, Individual default, merged saved-Supplier sections, hidden series, the five invoice columns, new inline supplier/contact/address creation with a paid draft, phone selection and detail filling, Supplier links, a correctly labelled payable card, stale-response rejection, zero-balance hiding, and mobile card/payment fit at 343 px on a 390 px viewport. The retained submitted purchase invoice remained unmodified. Temporary browser suppliers, their contacts/addresses, and the draft purchase invoice were removed; accounting test fixtures were rolled back and earlier retained demo records remain. Local migration completed, and Ruff lint/format, ESLint, JavaScript syntax, Python compilation, and diff whitespace checks passed.
- Remaining: Reload Desk for new form scripts and metadata. Normal master permissions and GL Entry read access apply. Production deployment has not been performed.

## 2026-10-23 — Reconcile local and GitHub main histories (Local)

- Changed: Merged the GitHub main commit into the local branch, retaining all nine local commits and the remote commit. Resolved the README overlap by keeping the development-site paragraph and the apps.yaml deployment instructions. Preserved the original local tip in `backup/main-before-sync-2026-10-23`.
- Checked: Before this tracking entry, the resolved tree matched the original local tree exactly. Confirmed apps.yaml, the build/deploy workflow, and the app-list renderer match the GitHub main versions. App-list rendering with a full commit SHA passed; Git whitespace and unresolved-conflict checks passed.
- Remaining: Push and production workflow/live-site verification are pending. No production deployment is claimed by this entry.


Add the newest update first. Each entry should state the change, the checks performed, and remaining work. Use **Local**, **Deployed**, or **Unverified** to make release status clear. Mark **Deployed** only after checking the production workflow and live site.

## 2026-10-23 — Show customer unpaid balance and hide invoice series (Local)

- Changed: Added an orange Sales Invoice card showing the selected customer's positive net receivable balance through today, in the invoice company's currency. A read-only endpoint checks Customer/Company access and Sales Invoice/GL Entry read permissions and applies GL row restrictions. The card refreshes on customer/company/form changes, hides for no customer or zero/credit balance, and rejects outdated responses. Added an Arabic card title. Hid Naming Series through the visibility snapshot and after native controller refresh, retaining its mandatory flag and native numbering. Setup preserves an existing series default or supplies Frappe's first configured series when absent. Applied the visibility setup twice on `elsakr-dev2.arab-erp.com`.
- Checked: Seven transaction-backed accounting tests passed: draft/cancelled exclusion, partial payments/full settlement, customer/date scope, company isolation, foreign invoice amounts in company currency, credit balance suppression, and Guest denial. All fixtures, including the temporary second company and foreign receivable account, were rolled back. Headless Chrome over development HTTPS verified an orange card with the retained demo customer's actual balance, hidden Naming Series with a populated default, automatic customer-name filling, hiding after clearing the customer, reselecting without duplicate cards, a 343 px card fitting a 390 px viewport, and rejection of a delayed earlier response after a newer zero result. The retained submitted invoice remained unmodified. The existing POS browser check also passed, including 400/600 allocation, zero outstanding, and desktop/mobile payment layout. Verified raw/effective Series Hidden flags, default, and fixture cleanup. Ruff lint/format, ESLint, JavaScript syntax, Python compilation, and diff whitespace checks passed.
- Remaining: Reload Desk for the updated script and translation. Users need GL Entry read access to see this card. No production deployment was performed.

## 2026-10-23 — Save Customer name and phone directly (Local)

- Changed: Hid Customer Salutation and the duplicate read-only Mobile No through the app-managed visibility snapshot. Added optional Phone immediately after Customer Name. Customer save now creates/selects the linked primary Contact automatically using normal permissions; matching linked contacts are reused and previous phone records are retained. Shared Contact phone values are preserved. Native contact selection/fetching remains available. New Customer forms hide the primary address/contact section until saved. Applied the setup twice on `elsakr-dev2.arab-erp.com`.
- Checked: Eleven transaction-backed tests passed: five Customer phone tests covering initial creation, optional phone/later addition, changes and reuse, native contact edits, and shared Contact preservation; all six existing inline-invoice customer tests also passed. Headless Chrome over development HTTPS verified hidden Salutation, visible Phone beside the name, Individual default, hidden primary-contact section on a new form, one-save Customer/Contact creation, direct phone changes, clean reopening with the saved number, and invoice phone search finding that Customer. Verified effective Hidden flags and Phone metadata. Removed the temporary browser Customer and both linked Contacts. Ruff lint/format, Python compilation, JavaScript syntax, and diff whitespace checks passed.
- Remaining: Reload Desk to load the new Customer form. Normal Contact permissions still apply. No production deployment was performed.

## 2026-10-23 — Link invoice customer, default POS, and set item columns (Local)

- Changed: Added an open-Customer icon beside the draft customer entry and a clickable Customer Name in read-only/submitted invoices, using the linked Customer ID. New Sales Invoices default Include Payment (POS) to 1 through an installation/migration setup hook. Initialized the Items grid to Item (2), المقاس (1), Quantity (1), Rate (2), Amount (2), including users with older grid preferences. Applied the defaults setup twice and cleared cache on `elsakr-dev2.arab-erp.com`.
- Checked: Headless Chrome over development HTTPS verified the new invoice POS default, visible payments, exact five column names/order/configured widths, draft customer link, and switching POS off. Opened retained submitted invoice `ACC-SINV-2026-00004`: Customer Name rendered a link, clicking it opened the correct Customer form, and the invoice stayed unmodified. Python compilation, Ruff lint/format, JavaScript syntax, and diff whitespace checks passed.
- Remaining: Reload Desk to load the form script. Production deployment has not been performed.

## 2026-10-23 — Enter invoice customers inline and preserve Customer layout (Local)

- Changed: Added one Customer Name autocomplete that searches permitted customers by name/ID and linked Contact phone, with optional Phone and Address immediately below it. Selecting an existing customer fills the details. Saving a new name creates an Individual Customer and optional linked Contact/Address inside the invoice transaction. Unique exact names and matching linked records are reused; ambiguous names require selection. Native Customer, receivable defaults, invoice validation, and accounting remain in use. Added focused regression tests. Captured the development Customer Hidden settings and Individual default, moved the primary address/contact section into Details, and hid the old Address & Contact tab. Freeform invoice addresses use company/site country without requiring or inventing a city; ordinary addresses retain the City requirement. Applied setup and full local migration on `elsakr-dev2.arab-erp.com`.
- Checked: Six transaction-backed regression tests passed, covering name-only creation/reuse, linked details and phone search, duplicate/blank names, rollback after failed invoice validation, regular-address City validation, and Guest permission denial. A separate name-only invoice insert populated the native receivable account and due date, then was rolled back. Headless Chrome over development HTTPS saved invoices from the three inline fields, searched by phone, selected the existing customer, and verified automatic phone/address filling. Browser checks confirmed Individual type, hidden Address & Contact tab, and visible primary address/contact fields in Details. Rechecked native 400/600 POS allocation, zero outstanding, desktop/mobile payment layout, and the retained submitted payment example. Freeform address rendering contains no missing-city placeholder. Ruff lint/format, Python compilation, JavaScript syntax, and diff whitespace checks passed. Temporary browser invoices and their synthetic customer/contact/address were removed; earlier retained demo records remain.
- Remaining: Reload Desk to load the updated form scripts and metadata. Normal Customer/Contact/Address permissions and a configured company/site country are required for creation. Production deployment has not been performed.

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
