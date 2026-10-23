import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import cint


class ElsakrSalesInvoice(SalesInvoice):
	def before_validate(self):
		from elsakr_app.invoice_customer import prepare_invoice_customer

		prepare_invoice_customer(self)

	def set_pos_fields(self, for_validate=False):
		pos = super().set_pos_fields(for_validate)
		if not cint(self.is_pos) or self.pos_profile or for_validate or not self.company:
			return pos

		# A POS Profile retains ERPNext's own payment selection and defaults.
		# Without one, offer enabled company methods with usable cash/bank accounts.
		method = frappe.qb.DocType("Mode of Payment")
		mapping = frappe.qb.DocType("Mode of Payment Account")
		account = frappe.qb.DocType("Account")
		methods = (
			frappe.qb.from_(method)
			.join(mapping)
			.on(mapping.parent == method.name)
			.join(account)
			.on(account.name == mapping.default_account)
			.select(method.name, method.type, mapping.default_account)
			.where(
				(method.enabled == 1)
				& (mapping.company == self.company)
				& (account.company == self.company)
				& (account.is_group == 0)
				& (account.disabled == 0)
				& account.account_type.isin(["Cash", "Bank"])
			)
			.orderby(method.name)
			.run(as_dict=True)
		)
		existing = {row.mode_of_payment for row in self.payments}
		for method in methods:
			if method.name not in existing:
				self.append(
					"payments",
					{
						"mode_of_payment": method.name,
						"type": method.type,
						"account": method.default_account,
						"amount": 0,
					},
				)
				existing.add(method.name)
		return pos
