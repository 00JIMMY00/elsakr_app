(() => {
	const paths = {
		sale: '<path d="M6 3h12v19l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6m-6 4h6m-6 4h3"/>',
		purchase:
			'<path d="M5 7h14l2 14H3L5 7Z"/><path d="M8 8V6a4 4 0 0 1 8 0v2m-4 4v6m-3-3 3 3 3-3"/>',
		stock: '<path d="m3 8 9-5 9 5v12H3V8Z"/><path d="M8 20v-8h8v8m-8-4h8M7 8h10"/>',
		catalog:
			'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><path d="M14 17h7m-7 4h7m-7-7h7"/>',
		accounts: '<path d="M4 21h16M6 17v-5m6 5V8m6 9V3M4 7l5-4 5 2 6-3"/>',
		expense:
			'<rect x="3" y="6" width="18" height="15" rx="3"/><path d="M3 10h18M7 6V3h10v3m-3 10h3"/>',
		arrow: '<path d="M19 12H5m6-6-6 6 6 6"/>',
		plus: '<path d="M12 5v14M5 12h14"/>',
	};
	const groups = [
		{
			id: "sales",
			title: "المبيعات والعملاء",
			icon: "sale",
			tone: "teal",
			items: [
				"Sales Invoice",
				"Daily Sales Summary",
				"Customer",
				"Accounts Receivable",
				"Accounts Receivable Summary",
				"Customer Group",
			],
		},
		{
			id: "purchases",
			title: "المشتريات والموردين",
			icon: "purchase",
			tone: "blue",
			items: [
				"Purchase Invoice",
				"Supplier",
				"Daily Purchase Summary",
				"Accounts Payable",
				"Accounts Payable Summary",
				"Supplier Group",
			],
		},
		{
			id: "stock",
			title: "المخزون والحركة",
			icon: "stock",
			tone: "amber",
			items: [
				"Stock Size Search",
				"Stock Balance",
				"Stock Ledger",
				"Stock Entry",
				"Warehouse",
				"Stock Reconciliation",
			],
		},
		{
			id: "catalog",
			title: "الأصناف والمقاسات",
			icon: "catalog",
			tone: "violet",
			items: ["Item", "Item Size", "Item Group"],
		},
		{
			id: "accounts",
			title: "الحسابات والأرباح",
			icon: "accounts",
			tone: "blue",
			items: [
				"Journal Entry",
				"Account",
				"Trial Balance",
				"Gross Profit",
				"Profit and Loss Statement",
			],
		},
		{
			id: "expenses",
			title: "المصروفات",
			icon: "expense",
			tone: "rose",
			items: ["Expense Entry", "Expense Entry Type", "Expense Entry Report"],
		},
	];
	const actions = [
		["Sales Invoice", "فاتورة بيع جديدة", "sale", "teal"],
		["Purchase Invoice", "فاتورة شراء جديدة", "purchase", "blue"],
		["Expense Entry", "تسجيل مصروف", "expense", "rose"],
		["Stock Entry", "حركة مخزون جديدة", "stock", "amber"],
	];
	const icon = (name) =>
		`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${
			paths[name] || paths.catalog
		}</svg>`;
	const reportsLast = (items) => [
		...items.filter((item) => item.type !== "Report"),
		...items.filter((item) => item.type === "Report"),
	];
	const escape = (value) => frappe.utils.escape_html(String(value));

	function href(item) {
		const route = frappe.utils.generate_route({
			name: item.link_to,
			type: item.type,
			doc_view: item.doc_view,
			is_query_report: item.is_query_report,
			report_ref_doctype: item.report_ref_doctype,
		});
		return route.split("/").map(encodeURIComponent).join("/");
	}

	function mount(root) {
		const el = root.querySelector(".ops");
		if (!el || el.dataset.mounted) return;
		el.dataset.mounted = "true";
		// Trim the native wrapper spacing only around this custom block.
		const widget = root.host?.closest(".custom-block-widget-box");
		if (widget) widget.style.padding = "0";
		const block = root.host?.closest(".ce-block__content");
		if (block) block.style.padding = "3px";
		const status = el.querySelector(".ops-status");
		const directory = el.querySelector(".ops-groups");

		function render(items) {
			const byTarget = new Map(items.map((item) => [item.link_to, item]));
			// The standard Workspace remains the registry; Frappe filters its shortcuts by permission.
			const available = groups
				.map((group) => ({
					...group,
					links: reportsLast(
						group.items.map((name) => byTarget.get(name)).filter(Boolean)
					),
				}))
				.filter((group) => group.links.length);
			const known = new Set(groups.flatMap((group) => group.items));
			const extra = items.filter((item) => !known.has(item.link_to));
			if (extra.length)
				available.push({
					id: "other",
					title: "أدوات إضافية",
					icon: "catalog",
					tone: "violet",
					links: reportsLast(extra),
				});
			directory.innerHTML = available
				.map(
					(group) => `
				<article class="ops-card ops-tone-${group.tone}" data-group="${group.id}">
					<header class="ops-card-header"><span class="ops-card-icon">${icon(group.icon)}</span><div><h3>${
						group.title
					}</h3></div><span class="ops-card-index" aria-hidden="true">${String(
						available.indexOf(group) + 1
					).padStart(2, "0")}</span></header>
					<nav aria-label="${group.title}">${group.links
						.map(
							(item, index) =>
								`<a class="ops-link${
									item.type === "Report" &&
									index > 0 &&
									group.links[index - 1].type !== "Report"
										? " ops-report-start"
										: ""
								}" href="${escape(href(item))}"><span>${escape(
									item.label
								)}</span><span class="ops-link-end">${
									item.type === "Report" ? "<small>تقرير</small>" : ""
								}${icon("arrow")}</span></a>`
						)
						.join("")}</nav>
				</article>`
				)
				.join("");
			const allowedActions = actions.filter(
				([doctype]) => byTarget.has(doctype) && frappe.model.can_create(doctype)
			);
			el.querySelector(".ops-actions").innerHTML = allowedActions
				.map(
					([doctype, title, symbol, tone]) =>
						`<a class="ops-action ops-tone-${tone}" href="${escape(
							href({ link_to: doctype, type: "DocType", doc_view: "New" })
						)}"><span class="ops-action-icon">${icon(
							symbol
						)}</span><span class="ops-action-copy"><strong>${title}</strong></span><span class="ops-action-plus">${icon(
							"plus"
						)}</span></a>`
				)
				.join("");
			el.querySelector(".ops-daily").hidden = !allowedActions.length;
			status.querySelector("span").textContent = items.length
				? `${items.length} أداة متاحة`
				: "لا توجد أدوات متاحة لحسابك. تواصل مع مسؤول النظام لضبط الصلاحيات.";
			status.classList.toggle("ops-status-quiet", items.length > 0);
		}

		async function load() {
			status.classList.remove("ops-status-quiet");
			status.querySelector("span").textContent = "جارٍ تحميل أدوات العمل…";
			el.querySelector("[data-retry]").hidden = true;
			directory.setAttribute("aria-busy", "true");
			try {
				const { message } = await frappe.call({
					method: "frappe.desk.desktop.get_desktop_page",
					args: {
						page: JSON.stringify({
							name: "Operations",
							title: "Operations",
							public: 1,
						}),
					},
				});
				if (!message?.shortcuts?.items) throw new Error("Missing Workspace shortcuts");
				render(message.shortcuts.items);
			} catch (error) {
				status.querySelector("span").textContent =
					"تعذّر تحميل الأدوات. يرجى إعادة المحاولة.";
				el.querySelector("[data-retry]").hidden = false;
			} finally {
				directory.setAttribute("aria-busy", "false");
			}
		}

		el.querySelector("[data-retry]").addEventListener("click", load);
		load();
	}
	window.elsakrOperationsWorkspace = { mount };
})();
