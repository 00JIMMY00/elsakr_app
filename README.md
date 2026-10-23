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


The **Operations** Workspace (`/app/operations`) groups 21 shortcuts into four
Arabic sections: customers and receivables, suppliers and payables, accounts
and invoices, and stock records and reports. It uses existing ERPNext permissions
and syncs during installation or migration. It is activated on the second local
development site; production deployment is pending.

The **Operations Dashboard** child Workspace (`/app/operations-dashboard`) shows top-selling Items, daily income and expenses, and total customer/supplier balances. Select a company and From/To dates; the initial range is month start through today. Customer and supplier balances are as of the end date. It is activated on the second local development site; production deployment is pending.

The **New** action opens the full form directly for Item, Customer, Supplier,
Sales Invoice, Material Request, Mode of Payment, and Item Size. This is active
on the second development site and will be applied to production by migration.

Items now support an optional **المقاس** (size) Link to the one-field **Item Size**
master, labelled **المقاس** in Arabic. Stock Balance and Stock Ledger include a
size filter that restricts their native calculations to matching Items. The
feature is activated on the second development site; production is pending.

Size is also shown automatically on sales/purchase transaction rows, stock
entries, reconciliation, material requests, and pick lists. The second development
site contains retained `DEMO-TYRE-*` Items and submitted demo transactions dated
2026-10-23 for manual testing; see CLIENT_UPDATES.md for balances and documents.

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
