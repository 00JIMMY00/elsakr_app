window.elsakrOperationsDashboard = window.elsakrOperationsDashboard || (() => {
	let filters = null;
	let requestKey = null;
	let request = null;
	const listeners = new Set();

	function getData(nextFilters, force = false) {
		const key = JSON.stringify(nextFilters);
		if (force || key !== requestKey) {
			requestKey = key;
			request = frappe.xcall("elsakr_app.operations_dashboard.get_dashboard", nextFilters).catch((error) => {
				requestKey = null;
				throw error;
			});
		}
		return request;
	}

	function notify() {
		for (const listener of listeners) listener(filters);
	}

	function format(value, currency) {
		return new Intl.NumberFormat(frappe.boot.lang || "ar", {
			style: "currency", currency: currency || "USD", maximumFractionDigits: 2
		}).format(value || 0);
	}

	function mountSummary(root) {
		const company = root.querySelector('[data-field="company"]');
		const fromDate = root.querySelector('[data-field="from_date"]');
		const toDate = root.querySelector('[data-field="to_date"]');
		const status = root.querySelector(".dashboard-status");
		const today = frappe.datetime.get_today();
		fromDate.value = filters?.from_date || `${today.slice(0, 7)}-01`;
		toDate.value = filters?.to_date || today;
		let current = 0;

		async function refresh(force = false) {
			if (!fromDate.value || !toDate.value || fromDate.value > toDate.value) {
				status.textContent = "تحقق من تاريخ البداية والنهاية";
				return;
			}
			const selected = {from_date: fromDate.value, to_date: toDate.value, company: company.value || undefined};
			const run = ++current;
			status.textContent = "جارٍ تحميل البيانات...";
			try {
				const data = await getData(selected, force);
				if (run !== current || !root.isConnected) return;
				filters = {...selected, company: data.company};
				company.replaceChildren(...data.companies.map((row) => {
					const option = document.createElement("option");
					option.value = row.name;
					option.textContent = row.name;
					return option;
				}));
				company.value = data.company;
				for (const name of ["revenue", "expenses", "receivables", "payables"])
					root.querySelector(`[data-value="${name}"]`).textContent = format(data[name], data.currency);
				status.textContent = `من ${data.from_date} إلى ${data.to_date}`;
				notify();
			} catch (error) {
				if (run === current) status.textContent = "تعذر تحميل لوحة المتابعة";
			}
		}
		root.querySelector('[data-action="refresh"]').addEventListener("click", () => refresh(true));
		refresh(false);
	}

	function mountCharts(root) {
		let current = 0;
		async function refresh(nextFilters) {
			if (!nextFilters) return;
			const run = ++current;
			try {
				const data = await getData(nextFilters);
				if (run !== current || !root.isConnected) return;
				const activity = root.querySelector('[data-chart="activity"]');
				const items = root.querySelector('[data-chart="items"]');
				const itemList = root.querySelector('[data-list="items"]');
				activity.replaceChildren();
				items.replaceChildren();
				itemList.replaceChildren();
				if (data.activity.length) {
					new frappe.Chart(activity, {type: "line", height: 260, colors: ["#249d76", "#e69b47"],
						data: {labels: data.activity.map((row) => row.day), datasets: [
							{name: "الإيرادات", values: data.activity.map((row) => Number(row.revenue || 0))},
							{name: "المصروفات", values: data.activity.map((row) => Number(row.expenses || 0))}
						]}});
				} else activity.textContent = "لا توجد قيود خلال الفترة";
				if (data.best_sellers.length) {
					new frappe.Chart(items, {type: "bar", height: 260, colors: ["#5373d7"],
						data: {labels: data.best_sellers.map((row, index) => String(index + 1)), datasets: [
							{name: "الكمية", values: data.best_sellers.map((row) => Number(row.qty || 0))}
						]}});
					for (const row of data.best_sellers) {
						const entry = document.createElement("li");
						entry.textContent = `${row.item_name || row.item_code} — ${Number(row.qty || 0)}`;
						itemList.appendChild(entry);
					}
				} else items.textContent = "لا توجد مبيعات خلال الفترة";
			} catch (error) {
				root.querySelectorAll("[data-chart]").forEach((element) => element.textContent = "تعذر تحميل الرسم");
			}
		}
		listeners.add(refresh);
		refresh(filters);
	}

	return {mountSummary, mountCharts};
})();
