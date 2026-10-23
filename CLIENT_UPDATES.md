# Elsakr client updates

The production site is `elsakr.arab-erp.com`. Its stack runs in Docker on
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

## Local development site

`elsakr-dev2.arab-erp.com` is a separate site in the local Bench at
`/home/xxx/bench1/my-bench`, with ERPNext and `elsakr_app` installed. It uses
the Bench web server on `http://localhost:8000`. Its public hostname is routed
through this machine's existing Cloudflare Tunnel to that service. The hostname
resolved in Cloudflare DNS and responded over HTTPS on 2026-10-23. Check
`https://elsakr-dev2.arab-erp.com/api/method/ping` when troubleshooting. The site's initial
Administrator password is stored locally in
`/home/xxx/.local/share/elsakr-dev2-admin-password` (mode `600`).

## Operations Workspace

For Item, Customer, Supplier, Sales Invoice, Material Request, Mode of Payment,
and Item Size, **New** opens the full form without an **Edit Full Form** step.
This is active on `elsakr-dev2.arab-erp.com`; reload Desk before trying it.
Production receives the change through the normal migration.

The app ships one public **Operations** Workspace at `/app/operations` with Arabic
sections for customers, suppliers, accounts, and stock. Its 21 shortcuts include
receivables/payables and their summaries, Trial Balance, Gross Profit, Stock
Balance, Stock Ledger, invoices, master records, Stock Entry, and Stock
Reconciliation. Tree shortcuts open accounts, warehouses, and master groups.
Access follows the user's existing ERPNext permissions.

The Workspace is activated on `elsakr-dev2.arab-erp.com`. Refresh Desk and select
**Operations**, or open `https://elsakr-dev2.arab-erp.com/app/operations`.
Standard Workspace JSON is synced by installation and `bench --site <site> migrate`;
the production rollout already runs migration. Production has not been deployed
for this change; use the normal release process above.

The Workspace uses **Operations** because ERPNext already reserves **Operation**
for a manufacturing DocType. A pre-model-sync patch renames the app's older
Workspace before the new JSON is synced. The rename keeps its saved layout and
shortcuts; reload Desk and use `/app/operations` after updating.

## Operations dashboard

Under **Operations**, open **Operations Dashboard** at `/app/operations-dashboard`. Select the company and dates and click **تحديث**. It opens from the first day of the current month through today. The top cards show posted revenue and expenses during that range, plus customer debt and supplier dues as of the ending date. The charts show daily revenue/expenses and the ten highest-selling Items by quantity from submitted Sales Invoices. Values use the selected company currency.

The dashboard is active on `elsakr-dev2.arab-erp.com` after local synchronization. Production deployment has not been performed. The user needs read permission for GL Entry, Sales Invoice, Company, and Custom HTML Block. Reload Desk after updating the app.

## Item sizes and stock report filters

On the second development site, open `/app/item-size` (Arabic: **المقاس**) to
maintain size names. Item/Stock/System Managers can maintain sizes; stock,
sales, purchase, and accounts users can read/select them. Each size has one
required unique field, **المقاس**. In Item, choose **المقاس** after Item Group;
this is an optional Link field, so existing Items need no immediate changes.

In **Stock Balance** (رصيد المخزن) or **Stock Ledger** (حركات المخزن), choose
**المقاس** to restrict results to Items currently assigned that size. Existing
item, group, brand, warehouse and date filters continue to apply. An unused
size or a conflicting Item selection returns no rows. Leave size blank for
standard report behavior. Changing an Item's size changes how historical
movements are classified by this filter.

Reload Desk after updating. Installation and migration sync the master and
create/update `Item.custom_size` automatically. The feature is active on
`elsakr-dev2.arab-erp.com`; production deployment remains pending.

## Transaction size columns and retained tyre demo

The **المقاس** column now appears in transaction rows and is read-only, fetched
from the selected Item. Coverage: sales/purchase quotations and orders, invoices
(including returns), Delivery Note, Purchase Receipt, Material Request, Stock
Entry, Stock Reconciliation, Pick List, and packed rows on supported sales
parents. Server validation also fills/corrects the value for API saves. Reload
Desk for fresh table metadata. Existing submitted transactions are not backfilled.

Retained development data on `elsakr-dev2.arab-erp.com`:

| Item code | Size | Final total quantity |
| --- | --- | ---: |
| DEMO-TYRE-175-70-R13 | 175/70 R13 | 20 |
| DEMO-TYRE-185-65-R14 | 185/65 R14 | 21 |
| DEMO-TYRE-195-65-R15 | 195/65 R15 | 29 |
| DEMO-TYRE-205-55-R16 | 205/55 R16 | 16 |

Use Item Group `DEMO Tyres`, date 2026-10-23, and warehouses `DEMO Tyres Main - T`
and `DEMO Tyres Branch - T` in Stock Balance / Stock Ledger. Branch holds one
unit of each Item; the remaining quantity is in Main. Submitted documents:

- Purchase invoice `ACC-PINV-2026-00001` with stock update, 09:00.
- Sales invoice `ACC-SINV-2026-00001` with stock update, 10:00.
- Stock receipts/transfer/issue: `MAT-STE-2026-00001`, `MAT-STE-2026-00002`,
  `MAT-STE-2026-00003`, at 11:00, 12:00, 13:00.
- Stock reconciliation `MAT-RECO-2026-00001`, 14:00.

All are synthetic demo data deliberately retained for manual testing. They
include accounting postings from the demo invoices. The creation helper refuses
other sites and repeat creation; it is not part of installation or migration.
No production deployment was performed.

Stock Balance and Stock Ledger also show **المقاس** as a Link column after
Item Name, whether or not the size filter is selected. The column uses the
current Item size and is included in report output for export. Refresh the report
to load the added column. This change is active on the second development site.

## Tyre model with size variants

The second development site includes template `DEMO-TYRE-MODEL-X` (كاوتش تجريبي
موديل X) and three native Item Variants under Item Group `DEMO Tyre Variants`:

| Variant code suffix | Size | Retained stock |
| --- | --- | ---: |
| 185-65-R14 | 185/65 R14 | 18 |
| 195-65-R15 | 195/65 R15 | 27 |
| 205-55-R16 | 205/55 R16 | 36 |

Open `/app/item/DEMO-TYRE-MODEL-X` to inspect the template and its variants.
Use the size-specific variant in invoices. Purchase invoice
`ACC-PINV-2026-00002` and sales invoice `ACC-SINV-2026-00002` are submitted and
retained for testing, dated 2026-10-23. For report testing select the new Item
Group and the date, then choose a size. Earlier standalone tyre demos remain.

For another model, enable Has Variants and use Item Attribute `Item Size`
(Arabic label المقاس). Add the desired values to this attribute and create
variants through ERPNext's Create action. Saving a variant automatically creates
a matching Item Size master if missing and selects it in the Item's size Link.
Existing size masters are reused. Normal Item Size create permission is required
for new masters. Templates have no single size and transactions use their variants.
This feature is active locally; production deployment is pending.

## Sales Invoice: Include Payment (POS)

**Include Payment (POS)** is selected by default on new Sales Invoices. Clear it
for a credit invoice. The native payment
table appears in **Details**, immediately below the customer/invoice header. Its
width is limited to 760 px and adapts to smaller screens. Enter the payment amount in
one method or split it across several methods. ERPNext calculates Paid Amount
and Outstanding Amount and posts each payment to its configured account.

An applicable POS Profile supplies its configured payment methods. Without a
profile, the app loads enabled methods mapped to an enabled company Cash/Bank
ledger account. Configure company mappings under **Mode of Payment**; profile
methods also need correct accounts. Reload Desk after updating the app.

On `elsakr-dev2.arab-erp.com`, retained submitted examples dated 2026-10-23 are
`ACC-SINV-2026-00003` (EGP 1,000 Cash) and `ACC-SINV-2026-00004` (EGP 400 Cash +
EGP 600 Credit Card). Each invoice totals EGP 1,000 with zero outstanding. The
development Credit Card mapping was corrected from Debtors to the new
`DEMO POS Bank - T` bank ledger. Both examples have balanced GL entries and no
stock movements. These are synthetic test records. Production deployment is
pending; the demo helper does not run on installation/migration.

Variant size detection also recognizes `Size` and `المقاس`. A variant with
exactly one attribute uses its full value as size even when the attribute is
named Colour. For multiple attributes, use one recognized size attribute.
Saving a variant generates its display name from the template name plus all
full attribute values, replacing abbreviation-based names. Item codes remain
unchanged. The reported Colour/White Item was repaired on the second development
site; other existing variants update on save.

## Sales Invoice visibility in both editors

On the second development site, **Edit DocType** now matches the existing
**Customize Form** Hidden settings for Sales Invoice: ten hidden fields/sections/
tabs, including Accounting Dimensions, Taxes, Tax Breakup, Pricing Rule Details,
Time Sheets, Payments and More Info tabs, Company Tax ID, Is Debit Note, and
Additional Discount Account. Five existing explicit visible settings remain:
Scan Barcode, Tax ID, In Words, Rounded Total, and Base Rounded Total.

POS payment methods remain available in **Details** even though the old Payments
tab is hidden. These 15 visibility settings are stored in the app and reapplied
after installation/migration. To change them permanently, update
`elsakr_app/sales_invoice_visibility.py`. Reload Desk after updating.
Production deployment is pending.

## Enter a customer directly on Sales Invoice

In **Customer Name**, search by name or phone and select an existing customer to
fill Phone and Address. Click the open icon beside a selected customer to open
the Customer record; after submission, the displayed Customer Name itself is
clickable. For a new customer, type the name and optionally enter
Phone and Address, add the invoice items, then Save. The app creates an
**Individual** Customer, a linked Contact when a phone is supplied, and a linked
Address when an address is supplied. No separate master forms are needed.
Only the customer name is required for this customer entry; normal invoice
requirements and master permissions still apply. Duplicate customer names must
be selected explicitly from the suggestions. Failed invoice saves roll back new
master records. Different supplied contact/address details add linked records
without overwriting existing primary records.

The simplified Customer form is preserved by the app, with primary address and
contact details in **Details** and the **Address & Contact** tab hidden. New
Customer forms default to **Individual**. App migration reapplies the captured
Customer Hidden settings from `elsakr_app/customer_setup.py`. Freeform invoice
addresses use the company's country (or site default) and need no separate City;
regular Address forms still require City. Reload Desk after updating.

This is applied on `elsakr-dev2.arab-erp.com`; production deployment is pending.

Sales Invoice Items open with these columns in order: **Item (2), المقاس (1),
Quantity (1), Rate (2), Amount (2)**. The numbers are the Configure Columns widths.
The app sets this layout when the form initializes, including for users with older
column preferences. Configure Columns can adjust it during the current form session.
Reload Desk to load these changes. Existing invoices keep their saved POS setting.
