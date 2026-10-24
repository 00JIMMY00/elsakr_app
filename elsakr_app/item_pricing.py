"""Expose native selling Item Prices on saved Item forms."""

import math

import frappe
from frappe import _
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import flt, nowdate


def setup_item_pricing():
	for prop, value, kind in (
		("label", "Selling Price", "Data"),
		("depends_on", "eval:!doc.has_variants && doc.is_sales_item", "Data"),
		(
			"description",
			"Save the Item to update its selling Item Price. Customer prices and pricing rules may change the invoice rate.",
			"Text",
		),
	):
		make_property_setter("Item", "standard_rate", prop, value, kind)
	frappe.clear_cache(doctype="Item")


def price_context(doc):
	from erpnext.stock.get_item_details import get_item_price

	defaults = {row.default_price_list for row in doc.item_defaults if row.default_price_list}
	price_list = next(iter(defaults)) if len(defaults) == 1 else None
	price_list = price_list or frappe.db.get_single_value("Selling Settings", "selling_price_list")
	price_list = price_list or "Standard Selling"
	context = frappe._dict(price_list=price_list, rate=0, name=None, modified=None)
	settings = frappe.db.get_value("Price List", price_list, ["selling", "enabled", "currency"], as_dict=True)
	if not settings or not settings.selling or not settings.enabled:
		context.error = _("Configure an enabled selling Price List in Selling Settings or Item Defaults.")
		return context
	context.currency = settings.currency
	if not frappe.has_permission("Item Price", "read"):
		context.error = _("Item Price read permission is required to view the selling price.")
		return context
	prices = (
		get_item_price(
			frappe._dict(price_list=price_list, uom=doc.stock_uom, transaction_date=nowdate()), doc.name
		)
		if not doc.is_new()
		else []
	)
	if prices:
		price = frappe.get_doc("Item Price", prices[0][0])
		price.check_permission("read")
		context.update(rate=price.price_list_rate, name=price.name, modified=str(price.modified))
		if len(prices) > 1 or flt(price.packing_unit) > 1:
			context.error = _("Multiple or quantity-specific prices apply. Manage these in Item Price.")
	return context


def load_selling_price(doc, method=None):
	if doc.has_variants or not doc.is_sales_item:
		return
	context = price_context(doc)
	doc.set_onload("selling_price", context)
	# standard_rate is only a creation shortcut upstream; Item Price is authoritative.
	doc.standard_rate = context.rate


def validate_selling_price(doc, method=None):
	if doc.is_new() or doc.has_variants or not doc.is_sales_item:
		return
	baseline = (doc.get("__onload") or {}).get("selling_price")
	previous = doc.get_doc_before_save()
	old_rate = baseline.get("rate") if baseline else previous.standard_rate
	if flt(doc.standard_rate) == flt(old_rate):
		return
	if not math.isfinite(flt(doc.standard_rate)) or flt(doc.standard_rate) < 0:
		frappe.throw(_("Selling Price must be zero or greater."))
	context = price_context(doc)
	if context.error:
		frappe.throw(context.error)
	if baseline and any(baseline.get(key) != context.get(key) for key in ("price_list", "name", "modified")):
		frappe.throw(_("The selling price changed. Reload the Item before editing its price."))
	doc.flags.selling_price_update = context


def save_selling_price(doc, method=None):
	context = doc.flags.pop("selling_price_update", None)
	if not context:
		return
	if context.name:
		price = frappe.get_doc("Item Price", context.name)
		price.price_list_rate = doc.standard_rate
		price.save()
	else:
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": doc.name,
				"price_list": context.price_list,
				"uom": doc.stock_uom,
				"price_list_rate": doc.standard_rate,
			}
		).insert()
