"""Resolve inline invoice customers inside the invoice's save transaction."""

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.desk.reportview import get_match_cond
from frappe.utils import cstr


@frappe.whitelist()
def search_customers(txt="", **kwargs):
	frappe.has_permission("Customer", "select", throw=True)
	# Contact permissions are required before searching or exposing phone numbers.
	phone_allowed = frappe.has_permission("Contact", "read")
	contact_match = get_match_cond("Contact") if phone_allowed else " AND 1=0"
	return frappe.db.sql(
		f"""select distinct c.name as value,
			case when c.name=c.customer_name then c.customer_name
			else concat(c.customer_name, ' (', c.name, ')') end as label,
			case when %(phone_allowed)s then coalesce(c.mobile_no, '') else '' end as description
		from `tabCustomer` c
		where c.disabled=0 and (c.name like %(txt)s or c.customer_name like %(txt)s
		or exists (select 1 from `tabDynamic Link` dl
			join `tabContact` on `tabContact`.name=dl.parent and dl.parenttype='Contact'
			join `tabContact Phone` p on p.parent=`tabContact`.name
			where dl.link_doctype='Customer' and dl.link_name=c.name
			and p.phone like %(txt)s {contact_match}))
		{get_match_cond('Customer').replace('`tabCustomer`', 'c')}
		order by c.customer_name, c.name limit 20""",
		{"txt": f"%{cstr(txt).strip()[:140]}%", "phone_allowed": phone_allowed},
		as_dict=True,
	)


@frappe.whitelist()
def customer_details(customer):
	doc = frappe.get_doc("Customer", customer)
	doc.check_permission("read")
	from frappe.contacts.doctype.address.address import get_default_address
	from frappe.contacts.doctype.contact.contact import get_default_contact

	contact = get_default_contact("Customer", customer)
	address = get_default_address("Customer", customer)
	phone, address_text = "", ""
	if contact:
		contact_doc = frappe.get_doc("Contact", contact)
		contact_doc.check_permission("read")
		phone = contact_doc.mobile_no or contact_doc.phone or ""
	if address:
		address_doc = frappe.get_doc("Address", address)
		address_doc.check_permission("read")
		address_text = "\n".join(filter(None, [address_doc.address_line1, address_doc.address_line2]))
	return {"name": doc.name, "customer_name": doc.customer_name, "phone": phone, "address": address_text}


def prepare_invoice_customer(doc):
	if doc.docstatus != 0:
		return
	entry = cstr(doc.get("custom_customer_entry")).strip()
	if not doc.customer and not entry:
		frappe.throw(_("Customer Name is required."))
	if not doc.customer:
		# Exact matches are reused, but duplicate display names require explicit selection.
		matches = frappe.get_list(
			"Customer", filters={"customer_name": entry, "disabled": 0}, pluck="name", limit_page_length=2
		)
		if len(matches) > 1:
			frappe.throw(_("Several customers have this name. Select one from the search results."))
		if matches:
			doc.customer = matches[0]
		else:
			customer = frappe.new_doc("Customer")
			customer.update({"customer_name": entry, "customer_type": "Individual"})
			customer.insert()
			doc.customer = customer.name
	customer = frappe.get_doc("Customer", doc.customer)
	customer.check_permission("read")
	if customer.disabled:
		frappe.throw(_("This customer is disabled."))
	doc.custom_customer_entry = customer.customer_name
	phone = cstr(doc.get("custom_customer_phone")).strip()
	address = cstr(doc.get("custom_customer_address")).strip()
	links = [{"link_doctype": "Customer", "link_name": customer.name}]
	if phone:
		contacts = frappe.get_all(
			"Dynamic Link",
			filters={"link_doctype": "Customer", "link_name": customer.name, "parenttype": "Contact"},
			pluck="parent",
		)
		contact_name = None
		for name in contacts:
			contact = frappe.get_doc("Contact", name)
			if any(row.phone == phone for row in contact.phone_nos):
				contact.check_permission("read")
				contact_name = name
				break
		if not contact_name:
			contact = frappe.get_doc(
				{
					"doctype": "Contact",
					"first_name": customer.customer_name,
					"is_primary_contact": not bool(contacts),
					"links": links,
					"phone_nos": [{"phone": phone, "is_primary_mobile_no": 1}],
				}
			)
			contact.insert()
			contact_name = contact.name
		doc.contact_person = contact_name
		doc.contact_mobile = phone
	if address:
		addresses = frappe.get_all(
			"Dynamic Link",
			filters={"link_doctype": "Customer", "link_name": customer.name, "parenttype": "Address"},
			pluck="parent",
		)
		address_doc = None
		for name in addresses:
			candidate = frappe.get_doc("Address", name)
			if "\n".join(filter(None, [candidate.address_line1, candidate.address_line2])) == address:
				candidate.check_permission("read")
				address_doc = candidate
				break
		if not address_doc:
			country = frappe.get_cached_value(
				"Company", doc.company, "country"
			) or frappe.defaults.get_global_default("country")
			address_doc = frappe.get_doc(
				{
					"doctype": "Address",
					"address_title": customer.customer_name,
					"address_type": "Billing",
					"address_line1": address.split("\n")[0],
					"address_line2": "\n".join(address.split("\n")[1:]),
					"country": country,
					"city": "",
					"custom_freeform_address": 1,
					"is_primary_address": not bool(addresses),
					"links": links,
				}
			)
			address_doc.insert()
		doc.customer_address = address_doc.name
		doc.address_display = get_address_display(address_doc.as_dict())

	# Keep native primary selectors aligned without replacing an existing primary.
	changed = False
	if doc.contact_person and not customer.customer_primary_contact:
		customer.customer_primary_contact = doc.contact_person
		customer.mobile_no = phone
		changed = True
	if doc.customer_address and not customer.customer_primary_address:
		customer.customer_primary_address = doc.customer_address
		customer.primary_address = doc.address_display
		changed = True
	if changed and customer.has_permission("write"):
		customer.save()
