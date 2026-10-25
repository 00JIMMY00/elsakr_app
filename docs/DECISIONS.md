# Decisions

Record lasting choices here. Add a new dated entry when a choice changes; keep the earlier entry for history.

## 2026-10-25 — Use the supplied animated WebP as the loader

**Decision:** Point native startup and blocking-request loaders at the supplied `tire-loader.webp`, preserving it byte-for-byte. Use its existing 40-frame, looping rotation with no additional CSS rotation. Keep the stationary SVG fallback for reduced-motion preferences and retain the current logo/favicon.

**Reason:** The user explicitly selected WebP and requested that the tire rotate around itself. Its animation already spins the wheel in place within a fixed 280 × 280 canvas.

**Consequence:** This supersedes the SVG loader selection. Versioned CSS refreshes cached loader references; migration reapplies the WebP splash setting. Native loading messages/counting/cleanup remain intact.

## 2026-10-25 — Use the supplied tire artwork for branding

**Decision:** Replace the newly drawn graphics with the user's `tire-loader.svg`, GIF, and WebP files. Use the SVG unchanged for loading animations and retain the other supplied formats unchanged. Derive the stationary logo by removing only animation metadata from the supplied SVG, and rasterize that artwork for the favicon. Use the stationary image for reduced-motion loading states.

**Reason:** The user clarified that their existing artwork must be used rather than newly designed graphics.

**Consequence:** This supersedes the custom artwork and warm login palette from the earlier branding change. No additional CSS rotation is applied to the already animated SVG. Native branding settings and Frappe loading lifecycles remain in use; filenames and versioned URLs refresh previously cached graphics.

## 2026-10-25 — Own Elsakr branding through native settings and scoped CSS

**Decision:** Store the logo and tire as app-owned SVG assets and the favicon as a multi-resolution ICO. Apply Website/Navbar branding settings after installation/migration, overriding shared theme identity. Use CSS for the native startup splash and blocking-request loader; keep Frappe's loading lifecycle and messages intact. Disable rotation for reduced-motion users.

**Reason:** The tire business needs a consistent Elsakr identity on login, Desk, browser tabs, and loading screens without upstream template or JavaScript changes.

**Consequence:** Migration reapplies this site's branding; lasting branding changes belong in this app. Shared theme defaults preserve the site-owned asset paths. Shared login CSS uses sufficient specificity to survive theme ordering, and its URL is versioned for proxy caches. Other application controls retain native styling and behavior.

## 2026-10-25 — Verify dashboard Workspace creation from standard source

**Decision:** Keep the standalone Operations Dashboard definition in standard Workspace JSON, alongside Operations. Verify that Frappe can create a missing Workspace from that file and expose its two blocks and sidebar entry. Keep the existing block installation/migration hook.

**Reason:** The development database contained the Workspace while Git contained only its blocks and assets; a successful production migration therefore left the route missing.

**Consequence:** New installations and migrations can create the dashboard without copying development database customization. Workspace layout changes must include this JSON in Git; block setup alone is insufficient. Production's immediate repair used the exact same definition through the native API.

## 2026-10-25 — Default Operations Dashboard to Today

**Decision:** Initialize the dashboard with Today selected and both dates set to today. Use today for omitted API date arguments. Keep manual presets/custom dates and an explicitly selected range within the open Desk session.

**Reason:** The user wants daily figures as the initial dashboard view.

**Consequence:** This supersedes the previous month-to-date default. Activity and sales initially cover today only; receivables/payables remain balances through the ending date. Existing permissions and calculations are unchanged.

## 2026-10-25 — Use concise, formal Operations copy

**Decision:** Show action labels and card headings without descriptive captions. Use formal Arabic for loading and error messages.

**Reason:** The user requested a professional workspace and removal or formalization of informal captions.

**Consequence:** Future Operations copy should remain concise and formal. This changes presentation only; native routes and permissions remain unchanged.

## 2026-10-25 — Open Operations directly with actions and cards

**Decision:** Remove the introductory banner and illustration, section headings, search input, and category filters from Operations. Keep the permission-aware quick actions and all six navigation groups, with native links and loading/access/error/retry handling.

**Reason:** The user requested a compact workspace without the introductory or search/filter sections.

**Consequence:** Available tools appear immediately. Search/filter rendering, listeners, and unused visual styles are removed; installation/migration refreshes the managed block. The underlying shortcut registry and permissions remain unchanged. This supersedes the banner and search/filter portions of the earlier shop-hub design.

## 2026-10-25 — Render Operations as a permission-aware shop hub

**Decision:** Keep the standard Operations Workspace and its 25 native shortcut definitions, rendering navigation in one app-managed Custom HTML Block with six Arabic groups, search/category filters, and four creation actions. Use Frappe's native `get_desktop_page` response for permitted shortcuts and its route generator for list/tree/report/new-form links. Gate creation actions on native Create permissions as well as shortcut availability. Install/migration updates the block's HTML/CSS/loader; custom visual assets are inline SVG and scoped shadow-root CSS.

**Reason:** The shop needs a recognizable tire/oil/battery identity and clearer daily navigation while preserving ERPNext's permission checks, forms, and reports. Frappe's supported Custom HTML Block provides layout control without changing upstream code or globally restyling Desk.

**Consequence:** The Workspace Shortcuts table remains the navigation registry, with group membership maintained in the app JavaScript; unfamiliar targets appear under additional tools. The native endpoint makes one extra navigation request when mounting the block. No counts, financial figures, or business-data writes are added. Direct edits to the managed block are replaced by migration; lasting visual changes belong in app sources. The existing standalone Operations Dashboard and site landing preference retain their separate roles. Production requires the normal migration and asset update.

Design references: [Frappe Workspaces](https://docs.frappe.io/framework/user/en/desk/workspace), the installed Frappe v15 Workspace/Custom Block/Shortcut implementations, and [Carbon navigation tiles](https://www.carbondesignsystem.com/building-blocks/core/components/tile/guidelines) for grouping, full-link targets, and keyboard focus.

## 2026-10-25 — Require a positive selling price

**Decision:** Require Selling Price greater than zero for both new and saved saleable Items and variants, using a conditional mandatory field and server validation before the unchanged-value check. Templates and non-saleable Items are exempt. Remove the explanatory caption while retaining price list, currency, and UOM context.

**Reason:** Item entry must specify a usable selling price, including when saving an existing Item with no price.

**Consequence:** Blank, zero, negative, and non-finite values cannot be saved through the Item flow. Existing unpriced saleable Items require a positive price on their next save; no existing records are backfilled. Native Item Price and invoice pricing behavior otherwise remain as recorded below.

## 2026-10-25 — Edit native selling prices from saved Items

**Decision:** Keep the native `standard_rate` control visible as Selling Price for saleable Items and variants, excluding templates. Load its value from the currently applicable general stock-UOM Item Price. Use the unique Item Defaults price list when present, otherwise Selling Settings (with Standard Selling fallback). On an explicit price edit, update/create the native Item Price in the Item save transaction with normal permissions. Show the list, currency, and UOM beside the control.

**Reason:** Upstream `standard_rate` is a creation shortcut hidden after insertion; Sales Invoices resolve Item Price records. Merely exposing the stored shortcut would display stale prices and would not update invoicing.

**Consequence:** Existing Item Prices remain authoritative. Unrelated saves preserve prices; stale price edits are rejected. Multiple active general prices or quantity-specific prices require the Item Price editor. Native customer/POS price-list selection, dates, UOM conversion, and pricing rules still determine final invoice rates; existing invoices are not repriced. New Item creation retains native price creation. No upstream source or invoice pricing engine is changed.

## 2026-10-25 — Use native site settings for the landing redirect and release popups

**Decision:** Manage a root-only HTTP 302 redirect to `/app/operations-dashboard` in Website Settings, and enable `disable_system_update_notification` and `disable_change_log_notification` in System Settings through installation/migration setup.

**Reason:** The site should open the operations overview and avoid repeated version announcements. Frappe already supports these behaviors without upstream edits or client overrides.

**Consequence:** Guests retain native login with the dashboard return destination. Other routes and permissions remain native. Migration reapplies these app preferences on sites using this app; permanent changes require updating `site_setup.py`. The 302 response avoids a permanently cached landing destination. Software updates continue through the existing release process.

## 2026-10-23 — Make the dashboard standalone and remove company selection

**Decision:** Clear the Operations Dashboard Workspace parent, remove the introductory header and company selector, and retain only date controls. Let the existing API select the permitted default company, retaining the returned company for subsequent requests.

**Reason:** The site has one company and the dashboard needs its own sidebar entry.

**Consequence:** The route and data permissions remain unchanged. Installation/migration syncs the standalone Workspace and managed blocks.

## 2026-10-23 — Prioritize phone use in the Operations dashboard

**Decision:** Keep the two existing Workspace HTML blocks and read-only API, with a navy/teal RTL layout, a derived revenue-minus-expenses overview, four existing totals, quick Today/Last 7 Days/This Month filters, collapsible company/date controls, and named horizontal ranking bars for the ten best sellers. Separate currency labels from amounts. Use daily lines for multiple activity dates and grouped bars for one activity date.

**Reason:** Phone users need a clear reading order, touch-sized filters, legible amounts, and product names beside their quantities. A single activity date cannot form a meaningful line.

**Consequence:** No ledger queries, permissions, or balance/date semantics change. The summary fetches once and shares loading/results/errors with the charts, rejecting older responses. The activity chart uses responsive inline SVG with an expandable exact-values table; this avoids the chart library’s animation errors inside Frappe shadow roots during resize/refresh. No comparative trends are inferred. Product quantities retain stock units, which can differ between Items. Install/migration continues to update the managed HTML blocks; the JavaScript is a shared app asset.

## 2026-10-23 — Mirror the simplified party flow in purchasing

**Decision:** Add a Supplier Name autocomplete plus optional Phone and Address to Purchase Invoice, with name/ID/linked-phone search and native Supplier navigation. Resolve new Individual Suppliers and their linked Contacts/Addresses during the invoice's `before_validate` using a Purchase Invoice subclass. Reuse unambiguous names and linked details, require selection for duplicate names, retain normal permissions and the invoice save transaction, and reuse the existing freeform-address mechanism. Add direct Supplier Phone entry with the same native Contact creation/reuse and preservation of old/shared phone records as Customer.

**Reason:** Purchasing should use the same short entry path as sales without opening Supplier, Contact, and Address separately.

**Consequence:** The Supplier and Purchase Invoice forms use app-managed visibility/defaults, hidden naming series with a valid native default, merged Supplier contact/address sections in Details, native Supplier links, and Item/size/quantity/rate/amount invoice columns. Supplier defaults to Individual. Supplier tax/default/info/portal and contact tabs are simplified along the existing Customer layout. Purchase Invoice hides the matching extra sections/tabs; supplier bill references and header withholding controls remain. Standard tax calculations and validations still run. Existing Sales Invoice/Customer code is retained.

**Decision:** Use the native Purchase Invoice Paid flow with its one payment method/account/amount section in Details. Retain the native unpaid default and payment accounting. Show an orange card for positive net payable balance (credit minus debit on Payable GL accounts) through today, in company currency, with the same permissions, company scope, zero/credit suppression, and stale-response protection as the sales card.

**Reason:** Purchase Invoice has a different payment model from Sales Invoice. Reusing it avoids introducing a separate payment ledger or marking new supplier purchases paid by default.

**Consequence:** Selecting Paid exposes the native payment controls in Details. The payable reminder includes posted purchases, payments, credits, and opening entries and is informational. It requires Purchase Invoice and GL Entry read permissions plus Supplier/Company access. Install/migrate applies all purchasing custom fields and metadata; future Purchase Invoice controller overrides need conflict review.

## 2026-10-23 — Show current customer debt on Sales Invoice

**Decision:** Show an orange card when the selected customer's net receivable balance is positive for the invoice company. Sum non-cancelled receivable GL debit minus credit through today in company currency, with payments, credits, and opening entries included. Check Customer and Company access and Sales Invoice/GL Entry read permission, applying GL match conditions. Refresh on selection/company/form refresh, immediately hide stale figures, and reject outdated responses.

**Reason:** Invoice entry needs a visible reminder of existing customer debt. Posted company-currency ledger amounts avoid mixing invoice currencies or ignoring receipts and credits.

**Consequence:** The card shows current net debt, including a saved submitted invoice's posted amounts, rather than an overdue-only total or a historical balance at the invoice date. Zero and credit balances show no warning. The feature is informational and does not block sales or alter accounting. Users need GL Entry read access; no permissions are widened.

**Decision:** Add Naming Series to the app's Sales Invoice Hidden snapshot. Preserve an existing series default; if absent, set Frappe's first configured series as the default so the mandatory hidden field remains valid. Rehide the control after native controller refresh, which otherwise reveals it on new forms.

**Consequence:** Existing invoice names, series options, and naming rules remain unchanged; new invoices continue to receive native generated names. This visibility/default is reapplied after install/migration.

## 2026-10-23 — Enter Customer phone directly beside the name

**Decision:** Add optional `Customer.custom_phone` directly after Customer Name, hide Salutation and the duplicate read-only Mobile No, and hide the primary address/contact section until the Customer is saved. A Customer `before_save` hook passes new numbers into ERPNext's native primary-contact creation. For an existing primary contact, reuse a matching linked Contact or create a new primary Contact without replacing the old phone record. Preserve shared Contact numbers. Keep native `mobile_no` and primary-contact fetching intact.

**Reason:** Creating a Customer with a phone should require one Customer save rather than a separate Contact form and link-selection step.

**Consequence:** The new Phone field is a convenience input; Contact remains the canonical phone record, and Sales Invoice phone search continues to use linked Contacts. Existing phones display without marking opened forms dirty. Blank convenience input preserves existing contact details. Normal Contact create/write/read permissions apply, and all writes stay in the Customer transaction. Installation/migration reapplies the added field and Hidden settings.

## 2026-10-23 — Default invoice POS and initialize the counter-sales grid

**Decision:** Apply `is_pos` default 1 through an app-managed Property Setter on install/migration. Initialize the Sales Invoice Item grid's in-memory GridView preference to Item/size/quantity/rate/amount with configured widths 2/1/1/2/2. Render read-only Customer Name as an escaped link to the actual Customer ID, with an open icon during draft entry.

**Reason:** New counter invoices should start with payment enabled and the requested item layout. Existing per-user grid settings would otherwise override the requested columns. Customer names must remain navigable after submission while retaining draft autocomplete.

**Consequence:** Saved POS values remain unchanged and users can clear POS on drafts. The grid starts with the app layout when the form initializes; Configure Columns remains usable during that form session. Links preserve Customer access checks and do not modify submitted invoices. ERPNext source is unchanged.

## 2026-10-23 — Enter and find invoice customers inline

**Decision:** Add a Customer Name autocomplete plus optional Phone and Address to Sales Invoice. Keep the native Customer Link behind the form and resolve new names during `before_validate`, inside the invoice transaction. Use native Customer, Contact, Address, party defaults, and invoice accounting. Search permitted customers by name/ID or any linked Contact phone. Reuse a unique exact name; require explicit selection for duplicate display names. Preserve existing primary records when adding different details.

**Reason:** Counter sales should not require opening three separate master forms. Deferring creation until invoice save avoids abandoned masters and lets failed saves roll back the new records.

**Consequence:** Normal master permissions apply; no elevated creation or separate commits are used. Customer creation defaults to Individual. The invoice client permits item entry with a new name and defers receivable-account/due-date requirements to native server defaults. Existing customer-specific pricing still uses native customer selection. Freeform invoice addresses store the supplied text without inventing a city; a hidden Address flag allows only these addresses to omit City, while a server hook preserves the requirement for regular addresses. Country comes from the invoice company or the site default. New primary selectors are filled where the user has Customer write permission. Existing primary contact/address records are not overwritten.

**Decision:** Capture the second development site's 16 hidden Customer fields/tabs (including its naming-series override), add the hidden Address & Contact tab, and move the existing primary address/contact section into Details with the native linked-record cards. Reapply visibility and the Individual default after install/migration.

**Consequence:** These Customer settings are app-owned and survive metadata synchronization. ERPNext source remains unchanged; other Customer properties remain outside the snapshot.

## 2026-10-23 — Open common records in full forms

**Decision:** Disable Quick Entry for Item, Customer, Supplier, Sales Invoice, Material Request, and Mode of Payment using DocType Property Setters applied on installation and migration. Disable it in the standard JSON for the app-owned Item Size DocType.

**Reason:** Frappe's New action uses Quick Entry when a DocType enables it, adding an Edit Full Form step for users who need the complete form.

**Consequence:** New actions for these seven DocTypes go directly to their full forms, including when launched from the Item list. No permissions or required fields change. The six ERPNext settings are app-managed and reasserted on migration; other DocTypes retain their current behavior.

## 2026-10-23 — Put the dashboard in a child Workspace with shared date filters

**Decision:** Ship a public child Workspace under Operations with two Custom HTML Blocks and one read-only API. Use posted GL Entries for income, expenses, receivables, and payables; use submitted Sales Invoice Items for the ten top sellers. The selected date range applies to activity and sales, while customer and supplier balances are measured through the end date. Scope all figures to one permitted company and its currency.

**Reason:** Frappe v15 Workspace chart widgets have separate date controls, while the requested dashboard needs one From/To filter across every section. A custom block can render the shared controls and charts inside the Workspace.

**Consequence:** Users need read access to GL Entry, Sales Invoice, Company, and the public Custom HTML Blocks. The API checks those permissions and applies Frappe match conditions to the queried records. The date range defaults to month start through today. Blocks are recreated or updated by install/migration hooks; direct edits to those two blocks are overwritten by a later migration.

## 2026-10-23 — Mirror requested Sales Invoice visibility in both editors

**Decision:** Ship an explicit snapshot of the 15 Sales Invoice Hidden overrides from the second development site's Customize Form: ten hidden and five visible. Apply these flags to both database DocFields (Edit DocType) and Property Setters (effective form metadata) after installation and migration. Update database field flags directly without saving/exporting ERPNext's standard DocType.

**Reason:** Edit DocType reads the standard field definitions and does not show Property Setter overrides as native field settings. The user requested the same Hidden settings in both editors.

**Consequence:** ERPNext source files remain untouched. An upstream metadata sync can reset the database flags, so the app reapplies the snapshot after migration. These 15 Hidden settings become app-maintained defaults; changes intended to survive migration need an update to the snapshot. Other customization properties, including print and mandatory settings, are preserved. Hiding is presentation only and grants/revokes no permissions.

## 2026-10-23 — Support single-attribute variants and full display names

**Decision:** Recognize `Item Size`, `Size`, and `المقاس` as size attributes. For a variant with exactly one attribute, use its value as size regardless of attribute name. Build variant display names from the template display name and all full attribute values during validation; preserve Item codes.

**Reason:** A user-created single-attribute Colour/White variant was excluded by the earlier canonical-only rule, and ERPNext's abbreviation-based display name obscured the full value.

**Consequence:** Single-attribute values, including colour names, can create size masters as requested. Multiple attributes use one recognized size attribute; multiple size attributes are rejected to avoid ambiguous classification. Saving variants refreshes their generated display names. Existing variants receive the change on save; only the reported Item was repaired immediately. Existing transaction row names are not backfilled.

## 2026-10-23 — Keep Sales Invoice POS payments in native accounting

**Decision:** Extend the ERPNext Sales Invoice controller only to load enabled, company-specific payment methods with non-group, enabled Cash/Bank accounts when no POS Profile applies. Preserve native profile payment selection, amount calculation, validation and GL posting. Correct the payment section collapse dependency in form metadata and open the native Payments table when POS is selected.

**Reason:** Users need to allocate invoice payment across one or more methods without a separate receipt workflow or duplicated accounting logic. The native `eval:!doc.is_pos` collapse dependency folds the section during refresh when POS is selected.

**Consequence:** Sites with a POS Profile continue to configure their methods there. Sites without one need company account mappings in Mode of Payment; new rows start at zero and existing allocations are retained. Invalid profile mappings still require operator correction. The development-only payment demo is explicit and never runs during migration. Future Sales Invoice controller overrides must be checked for conflicts.

## 2026-10-23 — Automatically create size masters when saving variants

**Decision:** When an Item variant uses the canonical `Item Size` attribute, create the matching Item Size master if absent, then assign `custom_size`. Reuse existing masters and tolerate duplicate insertion for concurrent variant creation. Keep normal master permissions and use the Item save transaction without committing separately.

**Reason:** The requested Create Variant workflow should require entering the size attribute value once, without separately creating the same size master.

**Consequence:** This supersedes the earlier requirement to create size masters manually first. Nonempty values are required. Users creating new size masters need the existing Item Size create permission; no roles are widened. Templates and unrelated attributes do not create sizes. A failed transaction rolls back both new records.

## 2026-10-23 — Use native Item Variants for multiple tyre sizes

**Decision:** Use ERPNext Item templates/variants with canonical Item Attribute `Item Size`. On Item validation, map the variant attribute to `custom_size`, require a matching Item Size master record, and clear the single-size field on templates using this attribute.

**Reason:** Every size needs its own inventory identity, while the template groups one tyre model. Reusing the existing size Link keeps transaction columns and stock report filters consistent with variant attributes.

**Consequence:** Variants remain separate stocked Items under one template. Ordinary Items retain their manual size classification. Users maintain matching master/attribute values before creating variants; validation does not create masters with elevated permissions. The new retained demo is separate from the earlier standalone tyre Items, so their transactions are preserved. The helper pins demo Item codes explicitly without changing the site's naming configuration.

## 2026-10-23 — Derive transaction size from the selected Item

**Decision:** Add a read-only size Link column to the 13 supported transaction child tables, use `fetch_from` for interactive selection, and synchronize Item sizes in parent validation for the 12 supported transaction types. Keep demo data creation explicit and restricted to `elsakr-dev2.arab-erp.com`.

**Reason:** The Item defines its size; showing a different editable size on an invoice or stock movement would contradict the Item identity and stock report filter. Server validation covers API-created transactions as well as the UI.

**Consequence:** Changing or clearing an Item on a draft row refreshes or clears its size. New saves/submissions store the current Item size, including return documents using the same transaction types. Existing submitted documents are not backfilled, and stock report filtering continues to use the current Item master classification. Demo purchases/sales affect accounting and inventory on the development site and are retained for the user's manual testing; migrations never create them.

## 2026-10-23 — Classify Items by a linked size master and filter native stock reports

**Decision:** Add standard `Item Size` (translated to «المقاس») with a single unique, required `size` field, and optional `Item.custom_size` Link. Create/update the Custom Field through installation and migration hooks. Extend the existing Stock Balance and Stock Ledger interfaces through a scoped `get_script` override and filter their execution through a Report controller subclass, delegating all other reports and unfiltered runs to Frappe.

**Reason:** Sizes need a reusable editable master. Applying the restriction before ERPNext computes stock preserves opening quantities, balances, and totals without maintaining copies of upstream reports or changing ERPNext source.

**Consequence:** Existing Items can remain without a size. Selecting a size intersects item/group/brand choices; zero matches produces an empty report rather than ERPNext's unrestricted empty-item behavior. Normal report permissions and calculations remain in place for interactive, exported, and prepared execution. Size is the Item's current classification, not a snapshot on each stock transaction. Item/Stock/System Managers can maintain sizes; stock, sales, purchase, and accounts users can read/select them. Future Report controller or `get_script` overrides from other apps must be checked for conflicts.

## 2026-10-23 — Use Operations to avoid the ERPNext Operation route

**Decision:** Rename the app Workspace to `Operations` (`/app/operations`) and ship a pre-model-sync patch for sites with the original app-owned `Operation` Workspace. Preserve Frappe's normal route validation.

**Reason:** ERPNext already has an `Operation` DocType. The original Workspace imported successfully but normal Desk saves raised `Name already taken, please set a new name` because both records shared `/app/operation`.

**Consequence:** The name and URL change to Operations. The patch preserves the existing layout and shortcuts when renaming and stops if a destination Workspace already exists, avoiding an automatic merge. Standard Workspace sync follows the normal app migration process. Manufacturing Operation records are unchanged.

## 2026-10-23 — Ship Operation as a standard app Workspace

**Decision:** Store one public `Operation` Workspace as standard JSON in the Elsakr App module, with four Arabic sections and shortcuts to existing ERPNext DocTypes and reports. Use Tree views for accounts, warehouses, and master groups.

**Reason:** The requested operations screen should travel with the app and use Frappe's native navigation and permission checks.

**Consequence:** Installation and migration sync the Workspace. Users see shortcuts allowed by their existing permissions; this change grants no additional access. Other Workspaces remain available. The initial activation targets the second local development site; production receives it through the normal release process.

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
