import json
import unittest
from pathlib import Path
from unittest.mock import patch

import frappe
from frappe.desk.desktop import get_desktop_page, get_workspace_sidebar_items
from frappe.modules.import_file import import_file_by_path

from elsakr_app.dashboard_setup import BLOCKS, setup_operations_dashboard


class TestDashboardWorkspace(unittest.TestCase):
	def test_missing_workspace_is_created_from_app_source(self):
		previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("dashboard_workspace_test")
		try:
			if frappe.db.exists("Workspace", "Operations Dashboard"):
				# Developer-mode deletion also removes the standard JSON from disk.
				with patch.dict(frappe.conf, {"developer_mode": 0}):
					frappe.delete_doc("Workspace", "Operations Dashboard", force=True)
			path = (
				Path(__file__).resolve().parents[1]
				/ "elsakr_app/workspace/operations_dashboard/operations_dashboard.json"
			)
			self.assertTrue(import_file_by_path(str(path)))
			setup_operations_dashboard()
			setup_operations_dashboard()
			workspace = frappe.get_doc("Workspace", "Operations Dashboard")
			self.assertEqual(workspace.module, "Elsakr App")
			self.assertEqual(workspace.public, 1)
			self.assertFalse(workspace.is_hidden)
			self.assertFalse(workspace.parent_page)
			self.assertFalse(workspace.for_user)
			self.assertFalse(workspace.roles)
			self.assertEqual([row.custom_block_name for row in workspace.custom_blocks], list(BLOCKS))
			self.assertEqual(
				[block["data"]["custom_block_name"] for block in json.loads(workspace.content)],
				list(BLOCKS),
			)
			frappe.clear_cache()
			page = get_desktop_page(json.dumps({"name": workspace.name, "public": 1}))
			self.assertEqual(
				{block.custom_block_name for block in page["custom_blocks"]["items"]}, set(BLOCKS)
			)
			sidebar = get_workspace_sidebar_items()
			self.assertIn(workspace.name, [page.name for page in sidebar["pages"]])
		finally:
			frappe.db.rollback(save_point="dashboard_workspace_test")
			frappe.clear_cache()
			frappe.set_user(previous_user)
