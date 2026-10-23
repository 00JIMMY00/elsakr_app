"""Save a Supplier's directly entered phone through native linked Contacts."""

import frappe
from frappe.utils import cstr


def sync_supplier_phone(doc, method=None):
	phone = cstr(doc.get("custom_phone")).strip()
	previous = doc.get_doc_before_save()
	primary_changed = previous and doc.supplier_primary_contact != previous.supplier_primary_contact
	phone_changed = not previous or phone != cstr(previous.get("custom_phone")).strip()

	# Native link fetching remains authoritative when a contact is selected or edited.
	if not phone or (primary_changed and not phone_changed) or (previous and not phone_changed):
		doc.custom_phone = doc.mobile_no or ""
		return

	doc.custom_phone = phone
	if phone == doc.mobile_no:
		return
	if not doc.supplier_primary_contact:
		# Supplier.on_update creates and links its primary Contact from mobile_no.
		doc.mobile_no = phone
		return

	# Reuse a matching linked Contact; preserve the old number and any shared Contact.
	contacts = frappe.get_all(
		"Dynamic Link",
		filters={"link_doctype": "Supplier", "link_name": doc.name, "parenttype": "Contact"},
		pluck="parent",
	)
	for name in contacts:
		contact = frappe.get_doc("Contact", name)
		if any(row.phone == phone for row in contact.phone_nos):
			shared = any(
				link.link_doctype != "Supplier" or link.link_name != doc.name for link in contact.links
			)
			if shared and (contact.mobile_no != phone or not contact.is_primary_contact):
				continue
			contact.check_permission("read")
			if not contact.is_primary_contact:
				contact.is_primary_contact = 1
				contact.save()
			break
	else:
		contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": doc.supplier_name,
				"is_primary_contact": 1,
				"links": [{"link_doctype": "Supplier", "link_name": doc.name}],
				"phone_nos": [{"phone": phone, "is_primary_mobile_no": 1}],
			}
		)
		contact.insert()
	# The matching phone may be a secondary number on a reused Contact.
	if contact.mobile_no != phone:
		for row in contact.phone_nos:
			row.is_primary_mobile_no = row.phone == phone
		contact.save()
	doc.supplier_primary_contact = contact.name
	doc.mobile_no = phone
