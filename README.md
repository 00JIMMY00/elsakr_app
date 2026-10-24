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


The **Operations** Workspace (`/app/operations`) is a compact Arabic shop hub with
four quick creation actions and six grouped navigation cards: sales/customers, purchases/suppliers,
stock movement, items/sizes, accounts/profit, and expenses. All 25 existing
shortcuts remain available under native ERPNext permissions; creation actions
also require Create permission. The responsive layout uses 16 px tool/action labels, 18 px card headings,
tighter card spacing, and dark mode. Actions and card headings use concise labels without descriptive captions.
The workspace ends after the cards, without a footer slogan.
Installation/migration syncs the standard Workspace and its app-managed HTML
block. It is activated on the second local development site; production
deployment is pending.

The **Operations Dashboard** standalone Workspace (`/app/operations-dashboard`) shows top-selling Items, daily income and expenses, and total customer/supplier balances. The phone-first Arabic layout includes a navy financial overview (revenue minus expenses), four balance/activity cards, and named product ranking bars. Use Today, Last 7 Days, or This Month, or expand **التواريخ** for custom dates; the initial range is month start through today. Customer and supplier balances are as of the end date. It is activated on the second local development site; production deployment is pending.

Opening `https://elsakr-dev2.arab-erp.com/` now redirects to Operations Dashboard,
with login first when needed. Version update and release change-log popups are
disabled site-wide. Reload open Desk sessions to load these preferences.
Installation/migration reapplies them; production deployment is pending.

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
