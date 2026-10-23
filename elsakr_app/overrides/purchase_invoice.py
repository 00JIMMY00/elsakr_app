from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice

from elsakr_app.invoice_supplier import prepare_invoice_supplier


class ElsakrPurchaseInvoice(PurchaseInvoice):
	def before_validate(self):
		super().before_validate()
		prepare_invoice_supplier(self)
