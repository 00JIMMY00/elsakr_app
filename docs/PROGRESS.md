# Progress

## 2026-11-16 — Verify the WhatsApp app installation (Production)

- Deployed: GitHub Actions run `43948152184` built the image and released
  commit `275e0a4`. The deploy log showed `frappe_waha` DocType sync reaching
  100%, followed by site migration and successful rollout completion.
- Checked live: The public Frappe endpoint returned `pong`. The WhatsApp app's
  Sales Invoice JavaScript asset returned HTTP 200.
- Remaining: None for the rollout repair.

## 2026-11-16 — Refresh site cache before installing new apps (Local verification)

- Changed: Run Frappe's site `clear-cache` before installing each new app. The
  failed production run reached the `frappe_waha` installation hook without
  loading `WAHA Settings`. Its rollback restored the site and the public ping
  returned `pong`.
- Checked locally: A stale module map made Frappe skip all `frappe_waha`
  definitions. Rebuilding the map let it discover 16, including `WAHA Settings`.
  Simulated rollouts passed for a new app, already installed apps, first install,
  and rollback after a cache-clear or app-install failure. Shell syntax and diff
  whitespace checks passed.
- Remaining: Verify the normal GitHub Actions release and the live site.

## 2026-11-16 — Show both invoice reports in Arabic (Local development)

- Changed: Both report titles, filters, grouping labels, table columns, statuses,
  summary cards, chart titles and payment actions now use Arabic even in English
  Desk sessions. Customer actions use تحصيل and supplier actions use سداد. Group
  option values retain their native keys and report tables use RTL direction.
  Customer/supplier names remain the saved record names. Updated current docs.
- Checked: All 15 customer/supplier database regression tests passed after updating
  the debit-note label expectation. Development HTTPS Chrome in an English Desk
  session verified Arabic columns/group choices/chart titles in both reports,
  unchanged party-bar totals and no JavaScript errors. Ruff lint/format,
  JavaScript syntax/Prettier and diff whitespace checks passed.
- Remaining: Reload development Desk to load the scripts. Production release is
  pending; no production deployment or accounting-document changes were made.

## 2026-11-16 — Show customers and suppliers on outstanding charts (Local development)

- Changed: Replaced ageing buckets in both invoice reports with one bar per
  customer/supplier, summing filtered invoice outstanding and sorting largest
  first. Duplicate display names include party IDs. Charts include all matching
  parties and use company currency. Added Arabic chart titles and updated current
  context, decisions, README and client notes.
- Checked locally: All 15 customer/supplier database regression tests passed.
  Focused chart checks verified aggregation across invoices, descending order,
  distinct parties with identical names, total preservation and empty results.
  Development HTTPS browser checks confirmed named customer/supplier bars and
  totals matching filtered invoices in both reports, with no JavaScript errors.
  Ruff lint/format and diff whitespace checks passed. Cleared development caches;
  no accounting records were saved or submitted.
- Remaining: Production deployment is pending. Reload the development reports to
  load the new charts. Overdue information remains in table columns and cards.

## 2026-11-16 — Add matching supplier invoice payments (Local development)

- Changed: Upgraded Simple Payable Summary to open Purchase Invoices with
  Supplier/Invoice/Supplier Group/Country grouping, expandable subtotals, native
  invoice/supplier links, supplier bill numbers, invoice total, paid, debit notes,
  outstanding, due dates/days overdue, Overdue Only, five cards and an ageing
  chart. Added matching Arabic labels and compact phone styling.
- Changed: Added Pay, Pay Supplier and checkbox Pay Selected Invoices actions.
  Supplier entries open unsaved native Pay Payment Entries with bank/cash as
  `paid_from` and payable account as `paid_to`. Current balances, permissions,
  same-party/company/account/currency and 200-invoice limits are enforced;
  invoice holds and native supplier payment holds are respected. The existing
  Payment Entry outstanding-invoice toolbar serves supplier entries too.
- Changed: Extracted shared native report/payment preparation into
  `invoice_balance_summary.py` and `invoice_payments.py`, retaining separate
  whitelisted customer/supplier endpoints. Updated context, decisions, README
  and client notes. The supplier view now excludes unallocated advances and
  standalone journal balances, replacing its prior net GL balance view.
- Checked locally: All 15 database tests passed: eight supplier tests and seven
  customer regression tests. Checked as-of payments/debit notes, Paid purchases,
  cancelled/future/draft/settled exclusions, company-currency amounts, four group
  modes and totals without double counting, overdue filtering, permission/empty
  results, native payment terms, single/multiple unsaved payments, fresh balances,
  mixed/invalid selections and supplier/invoice holds. Combined Pay entries passed
  native validation with a synthetic bank reference and zero difference. Ruff
  lint/format, Python compilation, JavaScript syntax/Prettier and diff whitespace
  checks passed. All accounting fixtures were rolled back; no test purchase
  invoices, suppliers or Payment Ledger rows remain.
- Checked in development HTTPS Chrome: Supplier table/cards/chart, all four group
  modes, one-invoice Pay, a checked three-invoice supplier group, matching amounts,
  zero difference, reference-replacement confirmation and actual native outstanding
  retrieval passed. Payments remained unsaved. Desktop and 390 px phone layouts
  had no document overflow. A temporary Arabic Accounts user verified translated
  RTL labels/layout without JavaScript errors and was removed. Navigating from
  supplier to customer report retained the correct customer endpoint and Receive
  entry; the final browser run recorded no JavaScript errors. Source was applied
  through the shared development Bench and site caches cleared; no migration or
  production workflow/image deployment was performed.
- Remaining: Production deployment is pending. Release both reports and the shared
  helpers/endpoints through the normal workflow, verify workflow/live site, and
  reload Desk. Review the native Pay entry before saving/submitting it.

## 2026-11-16 — Add invoice collections and native payment actions (Local development)

- Changed: Expanded Simple Receivable Summary with Customer/Invoice/Customer
  Group/Territory grouping, expandable subtotals, invoice/customer links, invoice
  total, paid, separate credits, outstanding, dates, overdue days/colors, Overdue
  Only, five cards and an ageing chart. Native ERPNext Accounts Receivable Payment
  Ledger calculations supply as-of amounts in company currency; totals count
  invoice rows once. Added Arabic translations and compact phone cards. Disabled
  chart animation after observing a native redraw error during resize/refresh.
- Changed: Added row Pay, group Pay Customer and checkbox Pay Selected Invoices.
  A permission-checked server mapper refreshes current balances and prepares an
  unsaved native Receive Payment Entry for up to 200 invoices sharing customer,
  company, receivable account and currency. Added a draft Payment Entry toolbar
  action for the native outstanding picker, with confirmation before replacing
  existing references. Updated decisions/context, README and client notes.
- Applied locally: Source is active on the shared development Bench. Cleared site
  and Payment Entry metadata caches on `elsakr-dev2.arab-erp.com`; no migration,
  business-document save/submission or production release was performed.
- Checked locally: Ten database regression tests passed (seven collection tests
  plus the three existing party-balance checks). Covered as-of receipts/credits,
  POS, cancellation/future/draft/settled exclusions, company currency, grouping
  without double counting, overdue filtering, permission/empty results, native
  payment terms, single/multiple receipt mapping, stale displayed balances and
  invalid/mixed selections. Combined receipts also passed native validation with
  a synthetic bank reference and zero difference. All accounting fixtures were
  rolled back; no test invoices, customers or Payment Ledger rows remain.
- Checked in development HTTPS Chrome: All four group modes, five cards, ageing
  chart, checkboxes, one-invoice Pay, a three-invoice checked customer group,
  matching allocations/zero difference, reference replacement confirmation and
  actual native outstanding-invoice retrieval worked. Receipts remained unsaved.
  Desktop and 390 px phone layouts had no document overflow. An Arabic Accounts
  user session showed translated labels and RTL layout; the temporary reviewer
  was removed. Final browser checks recorded no JavaScript errors. Ruff lint and
  format, Python compilation, JavaScript syntax/Prettier, payment toolbar
  draft/internal-transfer/submitted lifecycle and diff whitespace checks passed.
- Remaining: Production deployment is pending. Release app source/assets through
  the normal workflow, verify workflow and live site, then reload Desk. Report
  totals now cover open Sales Invoices, excluding unallocated advances and
  journal/opening balances; Simple Payable Summary retains net GL balances.

## 2026-11-06 — Remove footer side lines and center contact text (Live metadata and local source)

- Changed: Removed both decorative side-rule cells and their CSS, and centered
  the Arabic WhatsApp text beneath the attribution in both customer formats.
  Updated shared HTML/CSS, README, client notes, and context.
- Checked live: Both API saves and independent readbacks matched the sources,
  preserving other fields. Native synthetic rendering confirmed both side rules
  were absent and the WhatsApp destination was retained.
- Checked locally: Both A4-width Chrome previews confirmed centered contact text
  (zero horizontal center offset), no side-rule elements, and no footer overflow.
  Inspected the invoice footer screenshot. Diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source awaits a normal release;
  no workflow/image deployment or business-record creation was performed.

## 2026-11-06 — Show blue Arab-ERP.com attribution link (Live metadata and local source)

- Changed: Both customer print footers now show `بدعم من Arab-ERP.com` with a
  bold blue domain linking to the existing Arabic website destination. Updated
  shared HTML/CSS, README, client notes, and context.
- Checked live: Both format saves and independent readbacks passed, preserving
  other fields. Native unsaved synthetic previews confirmed the new label and
  `https://arab-erp.com/ar` destination.
- Checked locally: Both A4-width Chrome previews rendered the link in blue
  (`#2563eb`), weight 700, with no footer overflow. Inspected the invoice footer
  screenshot. Diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source awaits a normal release;
  no workflow/image deployment or business-record creation was performed.

## 2026-11-06 — Translate attribution and align footer rules (Live metadata and local source)

- Changed: Translated `powered by` to `بدعم من`, switched the branding row to
  Arabic RTL, and removed the repeated company name from the bottom footer in
  both shared formats. Centered both side rules by overriding native print-cell
  alignment/padding. Retained website and WhatsApp links. Updated shared sources,
  README, client notes, and context.
- Checked live: Both API saves and independent readbacks matched the shared
  sources with other fields preserved. Native synthetic previews verified Arabic
  attribution, both side rules, unchanged WhatsApp destination, no company name
  in the bottom footer, and the retained company name in the header.
- Checked locally: Chrome previews at A4 width showed no branding overflow;
  both rules align within 0.5 px of the branding center. Inspected the invoice
  footer screenshot. Diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source awaits a normal release;
  no workflow/image deployment or business-record creation was performed.

## 2026-11-06 — Replace footer phone link with Arabic WhatsApp contact (Live metadata and local source)

- Changed: Both formats now show `powered by عرب ERP` linking to the Arabic
  website `/ar`, including the logo link. Replaced the phone number/calling link
  with `تواصل معنا عبر واتساب`, matching the Arabic print layouts, linking to
  `https://wa.me/201097072200` for the same Egyptian number. Removed phone digit
  spacing from the contact style. Updated shared sources and operational notes.
- Checked live: Both format updates and independent readbacks passed, preserving
  other fields. Native rendering of unsaved synthetic previews verified the
  Arabic name/contact label, website/WhatsApp destinations, and no `tel:` link.
- Checked locally: Both A4-width Chrome previews had no footer overflow; inspected
  the invoice screenshot. A generated Chromium PDF retained the Arabic website
  and WhatsApp link destinations. Diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source awaits a normal release;
  no workflow/image deployment or business-record creation was performed.

## 2026-11-06 — Style Arab ERP print footer with logo and calling link (Live metadata and local source)

- Changed: Enlarged footer text to 13 px, added the supplied Arab ERP logo linked
  to the website, grey 12 px `01097072200` linked to `tel:01097072200`, and thin
  grey rules on both sides. Updated shared HTML/CSS and both production formats.
  Uploaded the original PNG as public site File `/files/arab_erp_logo.png`.
  Updated README, client notes, and context with the site-file dependency.
- Checked live: Public logo returned HTTP 200 with bytes matching the supplied
  image. Both format API updates and independent readbacks passed, preserving
  other fields. Native rendering of unsaved synthetic previews returned HTTP 200
  and verified the image, website/phone links, and two side rules for each format.
- Checked locally: Headless Chrome loaded both native-rendered previews with
  their print-format wrapper at A4 width; logo decoding passed and the center
  cell had no overflow. Inspected the invoice footer screenshot and generated
  a Chromium A4 PDF. Diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source awaits the next normal
  release; no workflow/image deployment was run. No business records were saved.
  Launching a phone app depends on the viewing device's configured calling app.

## 2026-11-06 — Add linked attribution to customer prints (Live metadata and local source)

- Changed: Added a centered English `powered by arab-erp.com` line at the end of
  both managed print formats, with the domain linking to `https://arab-erp.com/`.
  Updated shared HTML/CSS so migration preserves it, plus README and client notes.
- Checked live: Both original formats matched the app sources before editing.
  Native API updates and independent readbacks succeeded for Elsakr Sales Invoice
  and Elsakr Quotation; other record fields were preserved. Native rendering of
  unsaved synthetic documents returned HTTP 200 for both formats and confirmed
  the footer text, link destination, and placement in the final document footer.
  No business documents were created. Local diff whitespace checks passed.
- Remaining: Refresh open print previews. Local source needs inclusion in the
  next normal release. This was a direct live metadata update; no workflow/image
  deployment was run. Browser and PDF visual verification were not performed.

## 2026-11-06 — Simplify customer and supplier balance reports (Local development)

- Changed: Added Simple Receivable Summary and Simple Payable Summary with Name
  and Outstanding Amount columns; Company, Date, and Customer/Supplier filters;
  today defaults; company-currency net GL balances; positive balances only; and
  native company/party/GL permission checks. Repointed the two Operations summary
  shortcuts while preserving Arabic labels, updated their JavaScript grouping,
  and added Arabic report titles. Updated context, decisions, README, and client notes.
- Applied locally: Imported both Report definitions, changed only the two targets
  in the development Workspace, and cleared cache on `elsakr-dev2.arab-erp.com`.
  No full migration or bundle build was needed for this targeted synchronization.
- Checked: Three database regression tests passed for customers, suppliers, and
  permissions. Fixtures exercised payment/credit offsets, cancellation, date and
  company scope, account-type exclusion, missing/inaccessible parties, settled
  and credit balances, and Guest/unpermitted-company rejection; all fixtures were
  rolled back. Both installed reports executed successfully, returned exactly two
  columns, loaded their report scripts, and appeared in the native permitted
  Workspace response. The development HTTPS Workspace asset returned HTTP 200
  with both new targets. Python compilation, JSON parsing, JavaScript syntax,
  and diff whitespace checks passed.
- Remaining: Reload Desk and open the Operations shortcuts or new report URLs.
  Visual browser verification was not performed. Original ERPNext URLs still open
  the full native reports. Production deployment has not been performed.

## 2026-11-06 — Restrict dashboard expenses to Expense account type (Local)

- Changed: The Operations Dashboard activity query now includes expenses only
  when Account `account_type = "Expense"`, excluding Cost of Goods Sold, blank,
  and other types previously included by the Expense root classification. The
  expense card, daily chart, and revenue-minus-expenses net result share the
  filtered figure. Updated README, client notes, and the calculation decision.
- Checked locally: Executed the actual activity SQL against synthetic SQLite
  rows and confirmed Expense debits less credits, unchanged revenue, exclusion
  of COGS/blank/other types, company/date/cancelled filters, and an empty result
  for a COGS-only range. Python compilation and diff whitespace checks passed.
- Remaining: No Frappe/MariaDB integration or browser verification was performed.
  Production deployment has not been performed.

## 2026-11-03 — Complete delivery warehouse corrections (Live data)

- Changed: After production recovered, re-read both affected originals and
  confirmed no amendments existed. Created and submitted an amendment for the
  already-cancelled original. Native cancellation of the other submitted note
  was initially blocked because its source warehouse was disabled. Temporarily
  enabled that warehouse for native cancellation, immediately restored and
  verified its disabled state, then created/submitted the second amendment.
  Both amendments use مخزن ال31 - S in the header and every item row, retaining
  original invoice dates/times, item links, quantities, and rates. The other
  fourteen deliveries were retained.
- Checked live: All 16 active correction deliveries are submitted, fully billed
  against the existing invoices, and use the requested warehouse on every item
  row. Original dates and invoice delivered quantities match. The two originals
  are cancelled with no active stock/GL entries; the replacement/retained notes
  have 17 active Stock Ledger Entries matching their rows and 32 active GL Entries
  balanced across all 16 vouchers. Bin changes match the warehouse corrections,
  including reversing the remaining old-warehouse deduction. No negative Bin
  balances remain for the corrected item codes, and no Repost Item Valuation
  records were returned for the affected deliveries. Invoice totals, payments,
  advances, outstanding amounts, submitted status, and Update Stock flags remain
  unchanged. Restricted working snapshots and amendment mappings remain outside
  the repository; no private document/customer data or credentials are logged.
- Remaining: The warehouse correction is complete. Use the submitted amendments
  when opening the two corrected deliveries; cancelled originals remain as the
  native audit history. No default warehouse or negative-stock preference was
  changed. Updated current operational/context documentation; diff whitespace
  checks passed. No app code, image deployment, or workflow run was required.

## 2026-11-03 — Inspect delivery warehouse correction (Pending live availability)

- Requested: Use مخزن ال31 - S for the sales-stock correction deliveries.
- Observed: The target is an enabled non-group Warehouse in the same company.
  Fourteen original notes already use it. Two original notes contain a row from
  another warehouse: one is still submitted and the other was already cancelled
  when inspected, with no amendment and zero delivered quantity on its source
  invoice. Prepared the native cancel/amend flow to retain original dates,
  quantities, invoice/item links, and rates while assigning the target warehouse.
- Blocker: Before any correction mutation, the production API returned HTTP 502
  on the initial stock-balance read, followed by HTTP 530/Cloudflare Tunnel error
  1033 on repeated availability checks. No cancellation, amendment, or warehouse
  change was saved by this attempt. Restricted local inspection snapshots and
  the prepared helper remain outside the repository.
- Remaining: Restore production tunnel access, re-read current source/amendment
  states, and correct the two affected notes using native cancellation/amendment.
  Verify current stock/GL entries, invoice balances, and active delivery quantities
  afterwards. No app deployment or workflow run was performed. Diff whitespace
  checks passed.

## 2026-11-03 — Finish stock correction after negative stock was enabled (Live data)

- Changed: The user reported enabling negative stock and requested another
  attempt. Confirmed production Stock Settings.Allow Negative Stock was enabled,
  then submitted the same three existing linked draft Delivery Notes using native
  submission. No new documents or validation bypasses were introduced. After an
  interrupted response, checked the completed process and persisted results before
  further work; all 16 correction deliveries are now submitted.
- Checked live: Resource readback verified all 16 submitted notes, original
  invoice posting dates, full billing against existing invoices, and matching
  invoice-item delivered quantities. Their 17 active Stock Ledger Entries match
  all delivered item/warehouse quantities; current Bin changes match the complete
  correction. Their 32 active GL Entries balance across all 16 vouchers. No
  Repost Item Valuation records were returned for these deliveries. Invoice
  totals, payments, advances, outstanding amounts, submitted status, and Update
  Stock flags remain unchanged. Two item/warehouse balances are now negative
  under the user's setting. Updated current operational documentation; diff
  whitespace checks passed.
- Remaining: The requested delivery-note correction is complete; no correction
  drafts remain. Negative inventory balances need reconciliation with actual
  source stock records. The negative-stock setting remains site-owned. No app
  deployment, source-code change, or workflow run was required.

## 2026-11-03 — Correct production sales stock through linked deliveries (Live data)

- Scope: The production API returned 19 Sales Invoices with Update Stock disabled:
  16 submitted sales and three cancelled invoices, with no Delivery Notes. Native
  invoice-to-delivery mapping found 17 stock-item rows on the submitted invoices,
  with warehouse references and no prior deliveries, serials, batches, or
  supplier-direct deliveries. The user chose each invoice's original posting date.
- Changed: Created one native linked Delivery Note for each of the 16 submitted
  invoices, retaining the original posting date/time and invoice-item references.
  Submitted 13 through the native submit API. Three remain saved drafts because
  native NegativeStockError rejected stock issues for two items with zero
  recorded quantities. Negative-stock settings/validation were retained; cancelled
  invoices were excluded. No invoice was cancelled or recreated.
- Checked live: Readback verified all 16 document states, original dates, source
  links, and submitted invoice delivered quantities. All 13 submitted Delivery
  Notes are fully billed against their existing invoices. Their 13 active Stock
  Ledger Entries exactly match the submitted item/warehouse quantities, and
  current Bin changes match those movements. Their 26 active GL Entries balance
  across all 13 vouchers. No Repost Item Valuation records were returned for
  these deliveries. Invoice totals, payments, advances, outstanding amounts,
  submitted status, and Update Stock flags remained unchanged; draft deliveries
  have no active stock/accounting entries. Restricted local working snapshots
  hold the source/result/verification data; no customer data, document contents,
  or credentials are recorded here.
- Remaining: Correct the missing recorded stock from the appropriate source
  records before submitting the three linked draft deliveries. They have not
  updated stock. Updated client/operator guidance; no application code, workflow,
  or production image deployment was needed. Diff whitespace checks passed.

## 2026-11-03 — Add Quotation to production Operations (Live metadata)

- Changed: Added one native Quotation List shortcut labelled عروض الأسعار to
  production Operations and registered Quotation immediately after Sales Invoice
  in the المبيعات والعملاء card's existing inline block script. Retained all
  existing shortcuts/targets, including the saved stock-size report, and retained
  block HTML/CSS/access settings. Aligned current README/client/context status.
- Checked: Production resource readback verified 31 shortcuts, exactly one
  Quotation link, the script change, and preserved existing navigation/layout
  properties. The native permission-filtered desktop API returned the Quotation
  List shortcut. Authenticated production HTTPS Chrome confirmed exactly one
  عروض الأسعار link in المبيعات والعملاء after Sales Invoice, no sales-card
  overflow at 1440/390 px, and clicking opened the native Quotation List route
  with no page JavaScript errors. Reviewed the desktop screenshot. JavaScript
  syntax, Workspace JSON parsing, and diff whitespace checks passed. Saved
  restricted local metadata snapshots before changing the records; no snapshot
  contents or credentials are recorded here.
- Availability: Initial writes/readback encountered HTTP 502, then Cloudflare
  Tunnel error 1033 also affected SSH. On continuation, production returned HTTP
  200 and still had no Quotation shortcut; the successful update was then applied.
- Remaining: Refresh production Operations. No workflow/image deployment was run;
  this is a live metadata update. Include the existing local Workspace JSON and
  JavaScript changes in the next normal source release so migration retains the
  same registration.

## 2026-11-03 — Add Quotation to Operations sales navigation (Local)

- Changed: Registered one native Quotation List shortcut labelled عروض الأسعار in
  the standard Operations Workspace and placed it after Sales Invoice in the
  المبيعات والعملاء card. Updated the Workspace source timestamp and current
  README/client/context documentation to reflect 31 shortcuts. Existing native
  permission filtering, routing, and reports-last grouping remain in use.
- Applied: Synced the updated Workspace on `elsakr-dev2.arab-erp.com` and cleared
  its cache. The stored Workspace has 31 shortcuts and exactly one Quotation
  List link; the native permission-filtered desktop API returns that link.
- Checked: JavaScript syntax, Prettier, JSON parsing, and diff whitespace checks
  passed. Authenticated development HTTPS Chrome showed exactly one عروض الأسعار
  link in المبيعات والعملاء immediately after Sales Invoice. The sales card
  had no horizontal overflow at 1440/390 px; reviewed the screenshots. Clicking
  opened the native Quotation List route with no page JavaScript errors. Removed
  the temporary development review session.
- Remaining: Refresh Operations on the second development site. No production
  deployment or production metadata update was performed; a normal release must
  include the updated Workspace JSON and JavaScript asset.

## 2026-11-03 — Branded quotation and sales invoice prints (Local + live metadata)

- Changed: Added shared Arabic RTL A4 HTML/CSS and repeatable setup for Elsakr
  Quotation and Elsakr Sales Invoice, with native default Property Setters and
  installation/migration registration. Layouts reference the existing enabled
  elsakr logo Letter Head, display essential customer/item/size details and native
  totals, and conditionally include contact information, validity/due dates,
  discounts, tax, rounding, payments, submitted outstanding, and supplied terms.
  Draft/cancelled/credit-note labels and native print permissions are retained.
  Fixed logo sizing against native screen CSS and explicit total-amount contrast
  against the production PDF stylesheet. Aligned user/operator/context documents
  and recorded the maintenance decision.
- Checked locally: Four transaction-backed native rendering tests passed for
  repeatable setup/defaults, logo visibility, optional size columns, escaping,
  quotation validity, discounts/tax/rounding, cash/change/advances/write-offs,
  party-account currency, draft outstanding suppression, cancellations, signed
  credit notes, zero values, and 70-item output. Fixtures were rolled back. Native
  A4 PDFs generated for synthetic quotation/invoice and a 70-item quotation;
  reviewed the single-page layout and repeated item headings on page two of the
  five-page output. Both formats were then installed on the second development
  site. Ruff lint/format, Python compilation, CSS Prettier, and diff whitespace
  checks passed.
- Production application: Created only the two custom Print Formats through the
  authenticated native API and set their native defaults. Readback matched final
  app sources and both default Property Setters. Existing Letter Head/File records
  and business documents were retained. A restricted local metadata snapshot
  holds the preceding format/default state; no credentials or snapshot contents
  are recorded here.
- Checked live: Native API rendering passed for an existing submitted invoice and
  a synthetic unsaved quotation preview with the logo. The API returned no saved
  production quotations, and the supplied new-document route is unsaved. Default
  invoice rendering without an explicit format selected the new layout and logo;
  the site's native Letter Head visibility was already enabled. The live PDF
  endpoint generated a one-page A4 invoice; reviewed the final PDF including the
  corrected total contrast. Chrome review of both live-rendered layouts confirmed
  loaded, correctly proportioned logos, no horizontal content overflow, and no
  page JavaScript errors. An authenticated production HTTPS visit to the native
  invoice print page without an explicit format also returned HTTP 200, loaded
  the logo/default layout, and had no content overflow or page JavaScript errors;
  reviewed its screenshot.
- Remaining: Refresh open production forms before printing. No workflow/image
  deployment was run; this is a verified live metadata application. Commit and
  release the local sources so later installations/migrations manage the same
  layouts. The second development site's logo depends on its own Letter Head data.

## 2026-11-01 — Return retargeted stock-size report to its card (Local + live metadata repair)

- Cause: Production's Operations shortcut retained the label البحث عن مخزون المقاسات but targeted Stock Size Search 2, a saved Custom Report referencing Stock Size Search. The live JavaScript matched the local source and grouped by exact target, sending the new target to additional tools.
- Changed locally: Use the stable Arabic stock-search label to select the existing stock navigation slot, retaining the actual target for native routing. Other groups, report ordering, unknown shortcuts, and permission filtering retain their existing behavior. Updated current documentation and the lasting decision.
- Production repair: Updated only the managed Elsakr Operations Hub block's script through the authenticated native resource API, embedding the corrected app source for immediate use. Readback confirmed the exact script and unchanged HTML, CSS, access flags, and roles. Workspace/report records and business data were not modified. The restricted local repair snapshot contains the previous block for rollback; no credentials or snapshot contents are included here.
- Checked: Before applying, the production browser reproduced group `other`, and a browser-only corrected script put the link in group `stock`. After the saved repair, a fresh authenticated production HTTPS browser placed exactly one Stock Size Search 2 link immediately after جرد المخزون, with none under additional tools. Clicking opened the Stock Size Search 2 report route. Stock-card overflow checks passed at 1440/390 px; reviewed the desktop screenshot, with no page JavaScript errors during Workspace rendering. JavaScript syntax, Prettier, ESLint, and diff whitespace checks passed.
- Remaining: Reload the production Operations page. No workflow/image deployment was run; this is a verified live metadata repair. Include the source JavaScript fix in the next release, because migration reapplies the managed block's normal external asset loader. The production saved report/target remain site-owned; the source Workspace default remains Stock Size Search.


## 2026-11-01 — Restore the previous dashboard theme (Local)

- Changed: Restored the original navy/teal palette, gradient overview, soft rounded cards, and previous icon colors. Removed the tire-shop logo/tread and charcoal/amber styling. Retained purchasing totals, compact six-card sizing, three desktop columns, two phone columns, and tighter chart/ranking spacing. Refreshed both managed dashboard blocks on `elsakr-dev2.arab-erp.com` and aligned current documentation and the visual decision.
- Checked: Authenticated development HTTPS Chrome verified six cards, purchasing value matching the API, Today reset, no card/panel overflow at 1440/800/390/320 px, and no page JavaScript errors. Reviewed the restored desktop screenshot; light/dark screenshots were captured. Diff whitespace checks passed. Removed the temporary review session. No business records were saved.
- Remaining: Reload Desk on the development site. Production deployment has not been performed; normal release/migration must refresh both dashboard blocks and assets.


## 2026-11-01 — Purchasing card and compact tire-shop dashboard (Local)

- Changed: Added total purchasing for the selected inclusive interval from permission-filtered submitted Purchase Invoice company-currency grand totals, including taxes and signed returns. Missing purchase read access displays an unavailable state. Kept net result as revenue minus GL expenses. Replaced the large overview/four-card arrangement with six compact cards, three columns on desktop and two on phones. Added charcoal/amber styling, the supplied wheel identity, a CSS tread motif, tighter charts/rankings, and scoped native block padding. Retained 44 px date controls, presets, custom dates, RTL, dark mode, and shared fetching. Currency labels use the native configured symbol. Refreshed both managed blocks on `elsakr-dev2.arab-erp.com`; aligned user/operator/context documentation and decisions.
- Checked: Four database tests passed, covering inclusive date boundaries, signed returns, draft/cancelled exclusions, company scope, company-currency totals including taxes, empty periods, absent purchase read permission, invalid dates/company, Guest denial, and dashboard Workspace creation/repeated block setup. Fixtures were rolled back. Authenticated development HTTPS Chrome confirmed six cards, one initial data request, purchasing total matching the API for an existing historical interval, Today reset, successful responses, and no page JavaScript errors. Card/panel overflow checks passed at 1440/800/390/320 px; reviewed desktop, phone, and dark-mode screenshots. The final six-card grid measured 235 px high at 1440 px and 299/311 px at 390/320 px. Ruff lint/format, ESLint, Prettier, JavaScript syntax, Python compilation, and diff whitespace checks passed. Removed the temporary review session; browser checks saved no business records.
- Remaining: Reload Desk on the development site. Production deployment has not been performed. Normal release must serve the updated asset and migrate to refresh both managed HTML blocks and CSS. Purchasing is an invoice total rather than cash paid or an additional deduction from net result.


## 2026-11-01 — Edit Expense Entry rows directly (Local)

- Changed: Enabled native editable-grid metadata for Expense Entry Detail and in-place editing for Expense Entry's Expenses table through app-managed installation/migration Property Setters. Row clicks edit directly and the expanded-row button is hidden. The fetched account remains read-only. Applied on `elsakr-dev2.arab-erp.com`; updated README, client instructions, context, and decision.
- Checked: Repeated setup preserved both effective settings with exactly one setter per property and unchanged read-only account metadata. Authenticated development HTTPS Chrome confirmed clicking Amount opens an inline input, entering 123.45 updates the unsaved child model, and clicking Expense Entry Type exposes its inline Link input. No expanded row or row-editor button appeared; no JavaScript page errors occurred. Reviewed the desktop screenshot. No expense was saved. Ruff lint/format, Python compilation, and diff whitespace checks passed. Removed the temporary browser review session.
- Remaining: Reload Desk on the second development site. Production deployment has not been performed; the normal source release/migration applies these settings. Mobile interaction verification remains pending: the native grid requires horizontal touch scrolling to reach offscreen columns, which the automated check did not complete.


## 2026-11-01 — Arabic EGP symbol and stock purchasing/selling prices (Local)

- Changed: Added repeatable installation/migration setup for EGP's `ج.م` symbol and visible currency symbols, preserving currency codes. Applied setup on `elsakr-dev2.arab-erp.com`. Stock Size Search now keeps Item Name without the Item code column, shows current warehouse Bin valuation rate as Purchasing Price (MA) in company currency, and shows today's general stock-UOM selling price in its list currency. Added an optional selling-list override, 240/220 px price columns, Arabic purchasing label, and blank display for unavailable selling prices. Updated user/operator documentation and the lasting decision.
- Checked: Five focused database tests passed, covering report filters, positive/negative/zero stock, warehouse permissions, distinct warehouse costs, foreign-currency selling prices, date/UOM/party/batch/packing exclusions, ambiguous/missing prices, denied price access, Guest/company denial, and repeated symbol setup preserving currencies. Test records were rolled back. The development site's native valuation default is Moving Average. Authenticated development HTTPS Chrome confirmed seven columns with no Item code column, `ج.م`, and full `12,345,678.90` / `98,765,432.10` amounts inside their price cells using temporary browser-only sample values. Desktop and 390 px phone screenshots were reviewed; the native table scrolls horizontally. No page JavaScript errors occurred. Ruff lint/format, Python compilation, JavaScript syntax, CSV validation, and diff whitespace checks passed. Removed the temporary review session.
- Remaining: Production deployment has not been performed. The normal app release/migration applies the symbol and report source; reload Desk afterward. Purchasing cost uses the configured native valuation method and represents current warehouse cost rather than historical invoice COGS. Missing or ambiguous selling prices require maintenance in Item Price.


## 2026-10-31 — Add Payment Entry to Operations (Local)

- Changed: Added the native `Payment Entry` shortcut, labelled «قيد الدفع», to the الحسابات والأرباح card in the managed Operations Workspace. Updated the source Workspace timestamp so standard migration imports the new shortcut, and aligned the README, client instructions, project context, and decisions.
- Checked locally: JSON parsing, JavaScript syntax, and `git diff --check` passed. Migration completed successfully on `elsakr-dev2.arab-erp.com`; the stored Workspace has exactly 30 shortcuts and one Payment Entry shortcut with List view and the expected Arabic label. The stored Custom HTML Block still loads the Operations JavaScript asset. Production deployment has not been performed.
- Remaining: Reload the open Desk page to display the new shortcut. Production requires the normal source release and migration.

## 2026-10-29 — Organize Operations reports and add purchasing summary (Local)

- Changed: Grouped record links before reports in every Operations card, preserving each group's order and native permission filtering, with a subtle divider when both groups are visible. Added Daily Purchase Summary / تقرير المشتريات اليومي to the purchasing card (29 shortcuts total), matching the sales report's essential columns, supplier/date/status/type filters, today defaults/reset, four summary cards, colored statuses/amounts, and a blue daily chart. Submitted Purchase Invoices and signed returns use company-currency totals/current outstanding with native party-account currency handling. Synced the report/Workspace and refreshed the managed HTML Block on `elsakr-dev2.arab-erp.com`. Updated README, client instructions, context, and decisions.
- Checked locally: All four Operations report database integration tests passed with rolled-back fixtures, including purchasing submitted/draft/cancelled invoices, returns, supplier/status/type/date filters, empty results, invalid dates, both outstanding currency cases, unpermitted companies, and Guest denial. Native purchasing report execution/script loading succeeded and Operations returned 29 shortcuts. Authenticated development HTTPS Chrome verified reports last, exactly one divider for mixed cards, and no card overflow at 1440/390 px; the purchasing link opened its report, both dates initially matched today, a historical range rendered five existing invoices, four summary cards and a chart, and Today reset both dates. Reviewed desktop/phone screenshots; no JavaScript page errors occurred. Ruff lint/format, Prettier, JavaScript syntax, JSON parsing, and diff whitespace checks passed. Temporary browser session removed.
- Remaining: Reload Desk on the development site. Production deployment has not been performed; normal release must sync the report/Workspace, refresh the managed block's CSS, and serve the Operations JavaScript asset. Purchasing outstanding reflects current invoice balances, not an as-of-date payable balance.

## 2026-10-29 — Add simplified stock-size and daily sales reports (Local)

- Changed: Added standard Stock Size Search and Daily Sales Summary Script Reports, Arabic translations, and shortcuts in the Operations stock/sales cards (28 shortcuts total). Stock shows current Item/name/size/warehouse/quantity/unit with partial text search and exact Item/size/warehouse filters; zero balances are hidden and negative stock retained. Sales shows submitted invoices with essential columns, company/date/customer/status/sales-or-return filters, dynamic today defaults, a Today reset, four summary cards, a teal daily chart, and colored amounts/statuses. Returns reduce sales; values use company currency and current invoice outstanding, respecting ERPNext's party-account currency rules. Updated README, operator guide, project context, and decisions. Synced report/Workspace metadata on `elsakr-dev2.arab-erp.com`.
- Checked locally: Three database integration tests passed with rolled-back fixtures, covering size/warehouse/text/empty filters, negative and zero stock, a restricted Stock User's Warehouse User Permission, submitted/draft/cancelled sales, returns, date defaults/ranges/rejection, status/type/customer filters, both outstanding currency cases, unpermitted companies, and Guest denial. Native report `run` and `get_script` succeeded for both reports; the native Operations page response included both shortcuts. Authenticated development HTTPS Chrome verified today's initial sales dates, the Today reset, both rendered Operations links, four summary cards and a populated chart for a historical range, desktop and 390 px phone layouts, and no JavaScript page errors. Reviewed screenshots; native tables scroll horizontally on phones. Ruff lint/format, JavaScript syntax, JSON parsing, and diff whitespace checks passed.
- Remaining: Production deployment has not been performed. Reload Desk on the development site. Production requires the normal source release, metadata migration, and updated Operations asset. Stock reports current physical quantities; sales outstanding is current rather than an as-of-date receivables calculation.

## 2026-10-29 — Enable production Server Scripts (Live configuration)

- Changed: Enabled `server_script_enabled=true` in production's common Bench configuration and cleared the site cache. Added the same command to both the server's Compose configurator and `deploy/compose.yaml` for future deployments. Saved the previous common config and server Compose file under `/home/hassan/elsakr/config-backups/` with restricted access.
- Checked: Frappe's `is_safe_exec_enabled()` returned true and restricted Python evaluated a harmless arithmetic script successfully, with the verification transaction rolled back. Production HTTPS `/api/method/ping` returned `{"message":"pong"}`. The updated server Compose passed `docker compose config --quiet`.
- Release scope: Applied directly to the running production configuration; no image build, migration, or GitHub deployment was run. The repository commit deliberately uses `[skip ci]`; future normal releases include the configurator change. Reload Desk and use a System Manager account to create Server Scripts.

## 2026-10-26 — Add Expense Entry Report to Operations (Local)

- Changed: Added the existing Expense Entry Report to the standard Operations shortcut registry and the المصروفات card as تقرير قيود المصروفات. Reused the existing report link, badge, RTL layout, and native permission filtering. Synced the Workspace on `elsakr-dev2.arab-erp.com`, cleared cache, and aligned README, client instructions, and current context.
- Checked: Confirmed the development report is an enabled Script Report for Expense Entry. The native Workspace endpoint returns 26 shortcuts, including the report exactly once with query-report routing. Node rendering checks confirmed the report is in the expenses card with its encoded link and report badge, and omitted when excluded from the permission-filtered response. JavaScript syntax, JSON parsing, and diff whitespace checks passed.
- Remaining: Reload Desk to load the new shortcut and script. Visual browser review and production deployment were not performed; the normal release must sync the Workspace and JavaScript asset.



## 2026-10-25 — Make Operations the default landing workspace (Local)

- Changed: Root redirect now targets `/app/operations`; the app home-page hook points there too. Setup sets native Default Workspace to Operations for current System Users, and a User validation hook retains the default for future Desk users and later saves after native user-type calculation. Applied preferences on `elsakr-dev2.arab-erp.com`; updated current documentation and the lasting choice.
- Checked: Repeated setup retained exactly one root HTTP 302 redirect and the expected home hook/System User defaults. Focused checks verified the User hook registration and System User behavior while preserving Website User preferences. Development HTTPS Chrome verified the guest login return destination, authenticated root and `/app` and `/app/` opening Operations, logo navigation from Operations Dashboard and Customer list, and refreshing Operations. Explicit dashboard/Customer links remained accessible; no page JavaScript errors occurred. Python compilation and diff whitespace checks passed. Temporary verification session was removed.
- Remaining: Reload existing Desk sessions to receive the new native default. No production deployment was performed.

## 2026-10-25 — Switch loaders to the supplied rotating WebP (Local)

- Changed: Startup and native blocking-request loaders now use the supplied `tire-loader.webp`. Kept its existing centered rotation without adding a second CSS rotation. Updated the splash setting, CSS cache version, current documentation, and decision; reapplied branding on `elsakr-dev2.arab-erp.com`.
- Checked: Confirmed the repository WebP is byte-identical to the supplied file, loops indefinitely, contains 40 changing frames, and has identical centered visible bounds in every frame. Development HTTPS Chrome checks passed for WebP asset responses, startup/native blocking-loader references, reduced-motion still-image fallbacks, nested freeze/unfreeze cleanup, login at 1440/390/320 px, and existing logo/favicon, with no page JavaScript errors. Python compilation and diff whitespace checks passed. Removed the temporary development verification session.
- Remaining: Reload open sessions for the WebP loader. No production deployment was performed.

## 2026-10-25 — Replace custom graphics with supplied tire files (Local)

- Changed: Replaced the newly drawn logo/loader/favicon with the user's supplied tire artwork. Copied `tire-loader.svg`, `.gif`, and `.webp` unchanged into public branding assets. Native startup and blocking loaders use the already animated SVG; logo uses a still SVG derivative, and favicon uses that same artwork at four icon sizes. Removed the custom wordmark, wheel, and warm login palette, adjusted square logo sizing, and updated cache versions/settings and current documentation. Applied to `elsakr-dev2.arab-erp.com`.
- Checked: All three source copies are byte-identical. Chrome over development HTTPS verified the supplied SVG's changing rotation, reduced-motion animation suppression, stationary logo, login layout at 1440/390/320 px, Desk identity, favicon references, asset HTTP 200 responses, native nested freeze/unfreeze cleanup, and reduced-motion loader images. No page JavaScript errors occurred. Inspected the phone login screenshot and full favicon source render; verified favicon 16/32/48/64 px sizes. Python compilation and diff whitespace checks passed. Temporary development verification session was removed.
- Remaining: Reload open sessions to load the supplied artwork. No production deployment was performed.

## 2026-10-25 — Add Elsakr identity and spinning tire loader (Local)

- Changed: Added original charcoal/amber SVG Elsakr logo, tire emblem, and multi-resolution ICO favicon. Added shared Desk/website CSS for the logo, warm login styling, rotating startup tire, and native blocking-request loader, with reduced-motion support. Installation/migration applies native Website/Navbar Settings; versioned CSS avoids stale proxy caches. Applied branding twice on `elsakr-dev2.arab-erp.com`.
- Checked: Development HTTPS Chrome verified login at 1440/390/320 px without horizontal overflow, Desk logo, native favicon references, all three image assets returning HTTP 200, startup tire animation, reduced-motion suppression, and nested freeze/unfreeze cleanup. No page JavaScript errors occurred. Inspected login/loader screenshots and confirmed computed amber button/background styles after resolving shared-theme CSS precedence. Python compilation and diff whitespace checks passed.
- Remaining: Reload open sessions for the new identity. Production deployment has not been performed. Branding is app-managed and reapplied during migration; future asset edits should update the CSS version when needed.

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
