# Elsakr client updates

On 2026-10-25, production's missing **Operations Dashboard** Workspace was
restored from the same standard JSON now added to the local app source.
Authenticated Chrome verified both blocks and successful data loading at
`https://elsakr.arab-erp.com/app/operations-dashboard`. Reload Desk to refresh
the sidebar. Commit and push the source fix so future images include
`elsakr_app/elsakr_app/workspace/operations_dashboard/operations_dashboard.json`;
normal installation/migration then creates a missing Workspace automatically.
The existing setup hook manages its HTML blocks separately. This repair did
not deploy a new image; earlier pending-deployment notes reflect prior checks.

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

The public **Operations** Workspace at `/app/operations` opens directly with
quick actions for new sales invoices, purchase invoices, expenses, and stock
movements when the user has the matching read/create permissions. Six cards
organize all 25 existing shortcuts into sales/customers, purchases/suppliers,
stock movement, items/sizes, accounts/profit, and expenses. The introductory
banner, section headings, search box, category filters, and footer slogan have been removed.
Quick actions and card headings show concise labels without descriptive captions.
Loading/error messages use formal Arabic. Tree and report links retain their
native views and existing ERPNext permissions.
Tool and quick-action labels use 16 px text and card headings use 18 px.
Reduced card padding, smaller gaps, and trimmed native block spacing give the
labels more room. The layout adapts to phones and the selected Desk light/dark theme.

The Workspace is activated on `elsakr-dev2.arab-erp.com`. Refresh Desk and select
**Operations**, or open `https://elsakr-dev2.arab-erp.com/app/operations`.
Standard Workspace JSON and the **Elsakr Operations Hub** Custom HTML Block are
synced by installation and `bench --site <site> migrate`; the production rollout
already runs migration. The block's HTML/CSS/script loader are managed by
`elsakr_app.operations_workspace.setup_operations_workspace`; direct block edits
are overwritten by migration. The Workspace's Shortcuts table remains the
navigation registry; the app groups its permission-filtered response. Edit the
app sources for lasting layout changes. Production has not been deployed for
this change; use the normal release process above.

The Workspace uses **Operations** because ERPNext already reserves **Operation**
for a manufacturing DocType. A pre-model-sync patch renames the app's older
Workspace before the new JSON is synced. The rename keeps its saved layout and
shortcuts; reload Desk and use `/app/operations` after updating.

## Operations dashboard

Opening `https://elsakr-dev2.arab-erp.com/` redirects to
`/app/operations-dashboard` (HTTP 302). Logged-out users sign in first and then
return to the dashboard. Both **Disable System Update Notification** and
**Disable Change Log Notification** are enabled in System Settings. Reload open
Desk sessions to load these preferences. This is applied on the second
development site; production deployment is pending. Installation/migration
reapplies these app-managed settings through `elsakr_app.site_setup.setup_site_preferences`.
The existing software update/deployment process continues normally.

Open the standalone **Operations Dashboard** Workspace at `/app/operations-dashboard`. Use **اليوم**, **آخر ٧ أيام**, or **هذا الشهر** to refresh immediately. For a custom range, expand **التواريخ** (collapsed initially on phones), select the dates, and click **تحديث البيانات**. It opens with **اليوم** selected and both dates set to today. The top cards show posted revenue and expenses during that range, plus customer debt and supplier dues as of the ending date. The navy overview shows revenue minus expenses, with currency labels separated from amounts. The daily chart compares revenue/expenses (grouped bars for a single activity date); **عرض القيم اليومية** expands an exact-values table for the activity chart; the ranked list shows the ten highest-selling Items by quantity from submitted Sales Invoices, with names and quantities together. Quantities use stock units, which may differ between Items. Values use the selected company currency.

The dashboard is active on `elsakr-dev2.arab-erp.com` after local synchronization. Production deployment has not been performed. The user needs read permission for GL Entry, Sales Invoice, Company, and Custom HTML Block. Reload Desk after updating the app. For this dashboard redesign, installation/migration must refresh both managed HTML blocks as well as serving the updated app JavaScript; a script-only refresh does not update the stored HTML/CSS.

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
methods also need correct accounts. Reload Desk after updating the app. For this dashboard redesign, installation/migration must refresh both managed HTML blocks as well as serving the updated app JavaScript; a script-only refresh does not update the stored HTML/CSS.

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
**Customize Form** Hidden settings for Sales Invoice: eleven hidden fields/sections/
tabs, including Accounting Dimensions, Taxes, Tax Breakup, Pricing Rule Details,
Time Sheets, Payments and More Info tabs, Company Tax ID, Is Debit Note, and
Additional Discount Account, and Naming Series. Five existing explicit visible settings remain:
Scan Barcode, Tax ID, In Words, Rounded Total, and Base Rounded Total.

POS payment methods remain available in **Details** even though the old Payments
tab is hidden. These 16 visibility settings are stored in the app and reapplied
after installation/migration. To change them permanently, update
`elsakr_app/sales_invoice_visibility.py`. Reload Desk after updating.
Production deployment is pending.

## Enter a customer directly on Sales Invoice

New Sales Invoices keep the page at the customer header while the default POS
payment table opens below it. Typing a new Customer Name or replacing a selected
customer no longer raises the empty-address "Lead / Customer / Supplier" warning.
Reload Desk to load these fixes on the second development site; production
deployment is pending.

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

## Add a Customer with a phone in one save

On **Customer → New**, enter **Customer Name**, optionally enter **Phone** directly
below it, and Save. The app creates and selects the linked Contact automatically.
Salutation is hidden, Individual remains the default, and the primary
address/contact section appears after saving. Existing customers also show the
direct Phone input; saving a changed number selects a matching linked Contact or
creates a new primary Contact while retaining the previous number. Leaving Phone
blank preserves existing contact details. Invoice phone search finds these
customers through their linked Contacts. Normal Contact permissions apply.

Applied on `elsakr-dev2.arab-erp.com`. Reload Desk after updating. Production
deployment is pending; installation/migration preserves these settings.

## Customer unpaid-balance card

Selecting a Customer on Sales Invoice shows an orange card when they have a
positive unpaid balance in that invoice's company, formatted in company currency.
It shows the current net receivable balance through today, including receipts,
credits, opening entries, and posted invoices. It refreshes when the customer or
company changes or the form refreshes, and hides for zero/credit balances or no
customer. Users need read access to GL Entry, Sales Invoice, the Customer, and
the Company; existing record restrictions apply. This is an informational card.

**Naming Series** is hidden on Sales Invoice. Native numbering remains active;
if the site has no series default, setup uses its first configured series.
Applied on `elsakr-dev2.arab-erp.com`; reload Desk after updating. Production
deployment is pending.

## Faster Supplier and Purchase Invoice entry

**Supplier → New:** enter Supplier Name and optional Phone, then Save. New
suppliers default to Individual, and the linked Contact is created automatically.
Existing numbers can be changed directly; previous phone records are retained.
Contact/address cards and primary details appear in **Details** after saving.
The old Address & Contact tab and extra Supplier fields/sections are hidden.
Accounting and Settings remain available for account mappings and supplier holds.

**Purchase Invoice:** search Supplier Name by name or phone, or type a new name
with optional Phone and Address. Save the invoice to create and link the native
Supplier/Contact/Address automatically. Selecting an existing supplier fills its
details; use the open icon or read-only supplier name link to open its record.
Only the supplier name is required for this party entry; normal invoice and
master permissions and validations still apply. Duplicate names require explicit
selection, and failed invoice saves roll back new records.

The Item table starts with **Item, المقاس, Quantity, Rate, Amount** using widths
2/1/1/2/2. Naming Series is hidden with native numbering preserved. Supplier bill
number/date and header withholding controls remain available. Select **Is Paid**
to show native payment method, account, and amount controls in **Details**;
purchase invoices retain their native unpaid default. Payment accounting stays
native to Purchase Invoice.

An orange card shows what is currently owed to the selected supplier in the
invoice company, including posted purchases, payments, credits, and opening
entries through today. The amount uses company currency. Zero/credit balances
hide the card. Purchase Invoice/GL Entry read access and Supplier/Company access
are required; existing record restrictions apply.

These purchasing changes are applied on `elsakr-dev2.arab-erp.com`; reload Desk.
Installation/migration preserves them. Production deployment is pending.

Phone and Address on Sales Invoice and Purchase Invoice become read-only when an
existing customer or supplier is selected; they remain editable for a new inline
party. To change existing details, edit the Customer or Supplier record. Purchase
Invoice hides Apply TDS, Taxes and Charges Added, Taxes and Charges Deducted, and
Total Taxes and Charges. These form settings are active on the second development
site; reload Desk. Production receives them through migration.

The Operations Dashboard opens independently of Operations. It uses the single company automatically; there is no company selector or introductory header copy.

## Selling price on saved Items and variants

Open a saleable Item or size variant and edit **Selling Price** (**سعر البيع**),
then **Save**. Selling Price is required and must be greater than zero on new
and saved saleable Items and variants. The field remains visible after saving. It shows the current
selling Item Price, with its price list, currency, and stock unit beside it.
The list comes from the single Item Defaults price list when specified,
otherwise Selling Settings. Templates have no single selling price.

Sales Invoices use this Item Price as the base rate when they use the same
list, date, and unit. Customer/POS price lists, special customer prices, and
pricing rules can produce a different final Rate. Existing invoices keep their
rates. Multiple active general prices or quantity-specific prices must be
managed under **Item Price**. Normal Item Price permissions apply.

Applied on `elsakr-dev2.arab-erp.com`; reload Desk to load the field changes.
Production deployment is pending; installation/migration applies the metadata.
