window.elsakrOperationsDashboard = window.elsakrOperationsDashboard || (() => {
	let filters = null;
	let snapshot = null;
	const listeners = new Map();

	function notify(state) {
		snapshot = state;
		for (const [root, listener] of listeners) {
			if (root.isConnected) listener(state);
			else listeners.delete(root);
		}
	}

	function number(value) {
		return new Intl.NumberFormat(frappe.boot.lang || "ar", {maximumFractionDigits: 2}).format(value || 0);
	}

	function format(value, currency) {
		return new Intl.NumberFormat(frappe.boot.lang || "ar", {
			style: "currency", currency: currency || "USD", maximumFractionDigits: 2
		}).format(value || 0);
	}

	function setMoney(element, value, currency) {
		const parts = new Intl.NumberFormat(frappe.boot.lang || "ar", {
			style: "currency", currency: currency || "USD", maximumFractionDigits: 2
		}).formatToParts(value || 0);
		const amount = document.createElement("span");
		amount.className = "money-amount";
		amount.textContent = parts.filter((part) => part.type !== "currency").map((part) => part.value).join("").trim();
		const unit = document.createElement("small");
		unit.className = "money-currency";
		unit.textContent = parts.find((part) => part.type === "currency").value;
		element.replaceChildren(amount, unit);
	}

	function date(value, options = {day: "numeric", month: "short"}) {
		return new Intl.DateTimeFormat(frappe.boot.lang || "ar", options).format(new Date(`${value}T12:00:00`));
	}

	function mountSummary(root) {
		root = root.querySelector(".elsakr-dashboard") || root;
		if (root.dataset.mounted) return;
		root.dataset.mounted = "true";
		const fromDate = root.querySelector('[data-field="from_date"]');
		const toDate = root.querySelector('[data-field="to_date"]');
		const status = root.querySelector(".dashboard-status");
		const today = frappe.datetime.get_today();
		fromDate.value = filters?.from_date || today;
		toDate.value = filters?.to_date || today;
		root.querySelector("details").open = window.matchMedia("(min-width: 800px)").matches;
		let current = 0;

		function updatePeriods() {
			const week = frappe.datetime.add_days(today, -6);
			for (const button of root.querySelectorAll("[data-period]")) {
				const start = {today, week, month: `${today.slice(0, 7)}-01`}[button.dataset.period];
				button.setAttribute("aria-pressed", String(fromDate.value === start && toDate.value === today));
			}
		}

		async function refresh() {
			updatePeriods();
			if (!fromDate.value || !toDate.value || fromDate.value > toDate.value) {
				status.dataset.error = "true";
				status.textContent = "تحقق من تاريخ البداية والنهاية. الأرقام المعروضة تخص آخر فترة تم تحميلها.";
				return;
			}
			const selected = {from_date: fromDate.value, to_date: toDate.value, company: filters?.company || undefined};
			const run = ++current;
			root.setAttribute("aria-busy", "true");
			status.dataset.error = "false";
			status.textContent = "جارٍ تحميل البيانات…";
			root.querySelectorAll("[data-value]").forEach((element) => element.textContent = "—");
			root.querySelectorAll("[data-context]").forEach((element) => element.textContent = "—");
			notify({loading: true});
			try {
				const data = await frappe.xcall("elsakr_app.operations_dashboard.get_dashboard", selected);
				if (run !== current || !root.isConnected) return;
				filters = {...selected, company: data.company};
				for (const name of ["revenue", "expenses", "receivables", "payables"])
					setMoney(root.querySelector(`[data-value="${name}"]`), data[name], data.currency);
				setMoney(root.querySelector('[data-value="net"]'), Number(data.revenue) - Number(data.expenses), data.currency);
				root.querySelector('[data-context="company"]').textContent = data.company;
				root.querySelector('[data-context="period"]').textContent = `${date(data.from_date)} — ${date(data.to_date)}`;
				status.textContent = `${data.company} · ${date(data.from_date, {dateStyle: "medium"})} — ${date(data.to_date, {dateStyle: "medium"})}`;
				notify({data});
			} catch (error) {
				if (run !== current || !root.isConnected) return;
				status.dataset.error = "true";
				status.textContent = "تعذر تحميل لوحة المتابعة. حاول تحديث البيانات مرة أخرى.";
				notify({error: true});
			} finally {
				if (run === current) root.setAttribute("aria-busy", "false");
			}
		}
		root.querySelector("form").addEventListener("submit", (event) => {
			event.preventDefault();
			refresh();
		});
		for (const button of root.querySelectorAll("[data-period]")) {
			button.addEventListener("click", () => {
				fromDate.value = {today, week: frappe.datetime.add_days(today, -6), month: `${today.slice(0, 7)}-01`}[button.dataset.period];
				toDate.value = today;
				refresh();
			});
		}
		for (const input of [fromDate, toDate]) input.addEventListener("change", updatePeriods);
		refresh();
	}

	function renderActivity(container, data) {
		const rows = data.activity;
		const svgNS = "http://www.w3.org/2000/svg";
		function node(tag, attributes = {}, text) {
			const element = document.createElementNS(svgNS, tag);
			for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
			if (text !== undefined) element.textContent = text;
			return element;
		}
		const svg = node("svg", {viewBox: "0 0 600 270", role: "img", "aria-label": "الإيرادات والمصروفات اليومية؛ التفاصيل في جدول القيم أسفل الرسم"});
		const values = rows.flatMap((row) => [Number(row.revenue || 0), Number(row.expenses || 0)]);
		const low = Math.min(0, ...values);
		const high = Math.max(0, ...values);
		const span = high - low || 1;
		const y = (value) => 220 - (value - low) / span * 190;
		const x = (index) => rows.length === 1 ? 330 : 78 + index / (rows.length - 1) * 492;
		const compact = new Intl.NumberFormat(frappe.boot.lang || "ar", {notation: "compact", maximumFractionDigits: 1});
		for (let tick = 0; tick <= 4; tick++) {
			const value = low + span * tick / 4;
			svg.append(node("line", {x1: 74, x2: 580, y1: y(value), y2: y(value), stroke: "var(--dash-line)"}));
			svg.append(node("text", {x: 62, y: y(value) + 4, "text-anchor": "end", fill: "var(--dash-muted)", "font-size": 12}, compact.format(value)));
		}
		const labelStep = Math.max(1, Math.ceil(rows.length / 4));
		rows.forEach((row, index) => {
			if (index % labelStep === 0 || index === rows.length - 1)
				svg.append(node("text", {x: x(index), y: 250, "text-anchor": "middle", fill: "var(--dash-muted)", "font-size": 12}, date(row.day)));
		});
		for (const [field, color, label, offset] of [["revenue", "#087f73", "الإيرادات", -32], ["expenses", "#c27738", "المصروفات", 4]]) {
			if (rows.length > 1) {
				const points = rows.map((row, index) => `${x(index)},${y(Number(row[field] || 0))}`).join(" ");
				svg.append(node("polyline", {points, fill: "none", stroke: color, "stroke-width": 3, "stroke-linejoin": "round", "stroke-linecap": "round"}));
			}
			rows.forEach((row, index) => {
				const value = Number(row[field] || 0);
				const mark = rows.length === 1
					? node("rect", {x: x(index) + offset, y: Math.min(y(0), y(value)), width: 28, height: Math.max(2, Math.abs(y(value) - y(0))), rx: 5, fill: color})
					: node("circle", {cx: x(index), cy: y(value), r: rows.length > 45 ? 2 : 4, fill: color, stroke: "var(--dash-paper)", "stroke-width": 1.5});
				mark.appendChild(node("title", {}, `${date(row.day)} · ${label}: ${format(value, data.currency)}`));
				svg.appendChild(mark);
			});
		}
		container.appendChild(svg);
		const details = document.createElement("details");
		details.className = "activity-values";
		const summary = document.createElement("summary");
		summary.textContent = "عرض القيم اليومية";
		const table = document.createElement("table");
		const head = table.createTHead().insertRow();
		for (const label of ["التاريخ", "الإيرادات", "المصروفات"]) {
			const cell = document.createElement("th");
			cell.scope = "col";
			cell.textContent = label;
			head.appendChild(cell);
		}
		const body = table.createTBody();
		for (const row of rows) {
			const tr = body.insertRow();
			for (const text of [date(row.day), format(row.revenue, data.currency), format(row.expenses, data.currency)]) tr.insertCell().textContent = text;
		}
		details.append(summary, table);
		container.appendChild(details);
	}

	function mountCharts(root) {
		root = root.querySelector(".elsakr-dashboard") || root;
		if (root.dataset.mounted) return;
		root.dataset.mounted = "true";
		const activity = root.querySelector('[data-chart="activity"]');
		const itemList = root.querySelector('[data-list="items"]');

		function empty(element, message) {
			const state = document.createElement("div");
			state.className = "dashboard-empty";
			state.textContent = message;
			element.replaceChildren(state);
		}

		function render(state) {
			if (!state) return;
			root.setAttribute("aria-busy", String(Boolean(state.loading)));
			root.querySelector('[data-context="currency"]').textContent = state.data?.currency || "";
			if (!state.data) {
				const message = state.error ? "تعذر تحميل البيانات. أعد المحاولة من زر التحديث." : "جارٍ تحميل البيانات…";
				empty(activity, message);
				empty(itemList, message);
				return;
			}
			const data = state.data;
			activity.replaceChildren();
			itemList.replaceChildren();
			if (data.activity.length) {
				renderActivity(activity, data);
			} else empty(activity, "لا توجد قيود محاسبية خلال هذه الفترة");
			if (data.best_sellers.length) {
				const max = Math.max(...data.best_sellers.map((row) => Number(row.qty)), 1);
				data.best_sellers.forEach((row, index) => {
					const entry = document.createElement("li");
					const rank = document.createElement("span");
					rank.className = "item-rank";
					rank.textContent = number(index + 1).padStart(2, "0");
					const info = document.createElement("div");
					const name = document.createElement("span");
					name.className = "item-name";
					name.textContent = row.item_name || row.item_code;
					const track = document.createElement("span");
					track.className = "item-track";
					track.setAttribute("aria-hidden", "true");
					const fill = document.createElement("span");
					fill.className = "item-fill";
					fill.style.width = `${Math.max(0, Math.min(100, Number(row.qty) / max * 100))}%`;
					track.appendChild(fill);
					info.append(name, track);
					const quantity = document.createElement("span");
					quantity.className = "item-quantity";
					quantity.textContent = number(Number(row.qty));
					const unit = document.createElement("small");
					unit.textContent = "الكمية";
					quantity.appendChild(unit);
					entry.append(rank, info, quantity);
					itemList.appendChild(entry);
				});
			} else empty(itemList, "لا توجد مبيعات معتمدة خلال هذه الفترة");
		}
		listeners.set(root, render);
		render(snapshot || {loading: true});
	}

	return {mountSummary, mountCharts};
})();
