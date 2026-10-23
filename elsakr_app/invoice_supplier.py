"""Resolve inline invoice suppliers inside the invoice's save transaction."""

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.desk.reportview import get_match_cond
from frappe.utils import cstr


@frappe.whitelist()
def search_suppliers(txt="", **kwargs):
	frappe.has_permission("Supplier", "select", throw=True)
	# Contact permissions are required before searching or exposing phone numbers.
	phone_allowed = frappe.has_permission("Contact", "read")
	contact_match = get_match_cond("Contact") if phone_allowed else " AND 1=0"
	return frappe.db.sql(
		f"""select distinct c.name as value,
			case when c.name=c.supplier_name then c.supplier_name
			else concat(c.supplier_name, ' (', c.name, ')') end as label,
			case when %(phone_allowed)s then coalesce(c.mobile_no, '') else '' end as description
		from `tabSupplier` c
		where c.disabled=0 and (c.name like %(txt)s or c.supplier_name like %(txt)s
		or exists (select 1 from `tabDynamic Link` dl
			join `tabContact` on `tabContact`.name=dl.parent and dl.parenttype='Contact'
			join `tabContact Phone` p on p.parent=`tabContact`.name
			where dl.link_doctype='Supplier' and dl.link_name=c.name
			and p.phone like %(txt)s {contact_match}))
		{get_match_cond('Supplier').replace('`tabSupplier`', 'c')}
		order by c.supplier_name, c.name limit 20""",
		{"txt": f"%{cstr(txt).strip()[:140]}%", "phone_allowed": phone_allowed},
		as_dict=True,
	)


@frappe.whitelist()
def supplier_details(supplier):
	doc = frappe.get_doc("Supplier", supplier)
	doc.check_permission("read")
	from frappe.contacts.doctype.address.address import get_default_address
	from frappe.contacts.doctype.contact.contact import get_default_contact

	contact = get_default_contact("Supplier", supplier)
	address = get_default_address("Supplier", supplier)
	phone, address_text = "", ""
	if contact:
		contact_doc = frappe.get_doc("Contact", contact)
		contact_doc.check_permission("read")
		phone = contact_doc.mobile_no or contact_doc.phone or ""
	if address:
		address_doc = frappe.get_doc("Address", address)
		address_doc.check_permission("read")
		address_text = "\n".join(filter(None, [address_doc.address_line1, address_doc.address_line2]))
	return {"name": doc.name, "supplier_name": doc.supplier_name, "phone": phone, "address": address_text}


def prepare_invoice_supplier(doc):
	if doc.docstatus != 0:
		return
	entry = cstr(doc.get("custom_supplier_entry")).strip()
	if not doc.supplier and not entry:
		frappe.throw(_("Supplier Name is required."))
	if not doc.supplier:
		# Exact matches are reused, but duplicate display names require explicit selection.
		matches = frappe.get_list(
			"Supplier", filters={"supplier_name": entry, "disabled": 0}, pluck="name", limit_page_length=2
		)
		if len(matches) > 1:
			frappe.throw(_("Several suppliers have this name. Select one from the search results."))
		if matches:
			doc.supplier = matches[0]
		else:
			supplier = frappe.new_doc("Supplier")
			supplier.update({"supplier_name": entry, "supplier_type": "Individual"})
			supplier.insert()
			doc.supplier = supplier.name
	supplier = frappe.get_doc("Supplier", doc.supplier)
	supplier.check_permission("read")
	if supplier.disabled:
		frappe.throw(_("This supplier is disabled."))
	doc.custom_supplier_entry = supplier.supplier_name
	phone = cstr(doc.get("custom_supplier_phone")).strip()
	address = cstr(doc.get("custom_supplier_address")).strip()
	links = [{"link_doctype": "Supplier", "link_name": supplier.name}]
	if phone:
		contacts = frappe.get_all(
			"Dynamic Link",
			filters={"link_doctype": "Supplier", "link_name": supplier.name, "parenttype": "Contact"},
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
					"first_name": supplier.supplier_name,
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
			filters={"link_doctype": "Supplier", "link_name": supplier.name, "parenttype": "Address"},
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
					"address_title": supplier.supplier_name,
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
		doc.supplier_address = address_doc.name
		doc.address_display = get_address_display(address_doc.as_dict())

	# Keep native primary selectors aligned without replacing an existing primary.
	changed = False
	if doc.contact_person and not supplier.supplier_primary_contact:
		supplier.supplier_primary_contact = doc.contact_person
		supplier.mobile_no = phone
		changed = True
	if doc.supplier_address and not supplier.supplier_primary_address:
		supplier.supplier_primary_address = doc.supplier_address
		supplier.primary_address = doc.address_display
		changed = True
	if changed and supplier.has_permission("write"):
		supplier.save()
