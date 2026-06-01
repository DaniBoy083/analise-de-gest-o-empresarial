const appState = {
	data: null,
	charts: {},
};

const integerFormatter = new Intl.NumberFormat('pt-BR');
const decimalFormatter = new Intl.NumberFormat('pt-BR', {
	minimumFractionDigits: 1,
	maximumFractionDigits: 1,
});

function setChartDefaults() {
	if (typeof Chart === 'undefined') {
		return false;
	}

	Chart.defaults.color = '#a4ebbf';
	Chart.defaults.borderColor = 'rgba(45, 226, 127, 0.24)';
	return true;
}

function elementById(id) {
	return document.getElementById(id);
}

function safeText(id, value) {
	const node = elementById(id);
	if (node) {
		node.textContent = value;
	}
}

function escapeHtml(value) {
	return String(value)
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#039;');
}

function chartOrNull(key) {
	return appState.charts[key] ?? null;
}

function createOrReplaceChart(key, canvasId, config) {
	const canvas = elementById(canvasId);
	if (!canvas || typeof Chart === 'undefined') {
		return;
	}

	const existing = chartOrNull(key);
	if (existing) {
		existing.destroy();
	}

	appState.charts[key] = new Chart(canvas, config);
}

function renderSummary() {
	const data = appState.data;
	safeText('summaryText', data.executive_summary);
	safeText('datasetSource', `Fonte: ${data.meta.dataset_origin}`);
	safeText(
		'generatedAt',
		`Gerado em: ${new Date(data.meta.generated_at).toLocaleString('pt-BR')}`
	);
}

function renderKpis() {
	const kpis = appState.data.kpis;
	safeText('kpiTotalUnits', integerFormatter.format(kpis.total_units));
	safeText('kpiTotalModels', integerFormatter.format(kpis.total_models));
	safeText('kpiManufacturers', integerFormatter.format(kpis.total_manufacturers));
	safeText(
		'kpiTopManufacturer',
		`${kpis.top_manufacturer} (${decimalFormatter.format(kpis.top_manufacturer_share)}%)`
	);
	safeText('kpiCagr', `${decimalFormatter.format(kpis.growth_cagr)}%`);
	safeText('kpiRecommendedState', kpis.recommended_state);
}

function renderLists() {
	const insightsNode = elementById('insightsList');
	const recommendationsNode = elementById('recommendationsList');

	if (insightsNode) {
		insightsNode.innerHTML = appState.data.insights
			.map((item) => `<li>${escapeHtml(item)}</li>`)
			.join('');
	}

	if (recommendationsNode) {
		recommendationsNode.innerHTML = appState.data.recommendations
			.map((item) => `<li>${escapeHtml(item)}</li>`)
			.join('');
	}
}

function renderTopModels() {
	const tableBody = elementById('topModelsTable');
	const modelLimit = Number(elementById('modelLimit')?.value || 12);
	safeText('modelLimitValue', String(modelLimit));

	if (!tableBody) {
		return;
	}

	const rows = appState.data.tables.top_models.slice(0, modelLimit);
	tableBody.innerHTML = rows
		.map(
			(row) =>
				`<tr>
`
				+ `<td data-label="Modelo">${escapeHtml(row.modelo)}</td>
`
				+ `<td data-label="Fabricante">${escapeHtml(row.fabricante)}</td>
`
				+ `<td data-label="Quantidade">${integerFormatter.format(row.quantidade)}</td>
`
				+ `<td data-label="Market Share (%)">${decimalFormatter.format(row.market_share)}</td>
`
				+ `</tr>`
		)
		.join('');
}

function selectedFastFilter() {
	return Number(elementById('stateFastFilter')?.value || 0);
}

function filteredStates() {
	const threshold = selectedFastFilter();
	return appState.data.tables.top_states.filter((row) => row.fast_dc_rate >= threshold);
}

function renderTopStates() {
	const tableBody = elementById('topStatesTable');
	const threshold = selectedFastFilter();
	safeText('stateFastFilterValue', `${threshold}%`);

	if (!tableBody) {
		return;
	}

	const rows = filteredStates();
	if (!rows.length) {
		tableBody.innerHTML = '<tr><td class="table-empty" colspan="6">Nenhum estado atende ao filtro selecionado.</td></tr>';
		return;
	}

	tableBody.innerHTML = rows
		.map(
			(row) =>
				`<tr>
`
				+ `<td data-label="Estado">${escapeHtml(row.estado)}</td>
`
				+ `<td data-label="Estacoes">${integerFormatter.format(row.stations)}</td>
`
				+ `<td data-label="Cidades">${integerFormatter.format(row.cities)}</td>
`
				+ `<td data-label="Fast DC (%)">${decimalFormatter.format(row.fast_dc_rate)}</td>
`
				+ `<td data-label="Potencia Media (kW)">${decimalFormatter.format(row.avg_power_kw)}</td>
`
				+ `<td data-label="Score">${decimalFormatter.format(row.attractiveness_score)}</td>
`
				+ `</tr>`
		)
		.join('');
}

function renderManufacturerChart() {
	const chartType = elementById('manufacturerChartType')?.value || 'doughnut';
	const source = appState.data.charts.manufacturer_share;
	createOrReplaceChart('manufacturerChart', 'manufacturerChart', {
		type: chartType,
		data: {
			labels: source.labels,
			datasets: [
				{
					label: 'Unidades',
					data: source.values,
					backgroundColor: ['#2de27f', '#1cc86e', '#12ae5f', '#0e8e4d', '#0a723f', '#085c34', '#09482a', '#0a331f'],
					borderColor: '#04180d',
					borderWidth: 1,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					position: chartType === 'doughnut' ? 'bottom' : 'top',
				},
			},
			scales: chartType === 'bar'
				? {
						y: {
							beginAtZero: true,
						},
					}
				: {},
		},
	});
}

function renderYearlyChart() {
	const source = appState.data.charts.yearly_sales;
	createOrReplaceChart('yearlySalesChart', 'yearlySalesChart', {
		type: 'line',
		data: {
			labels: source.labels,
			datasets: [
				{
					label: 'Vendas por ano',
					data: source.values,
					borderColor: '#2de27f',
					backgroundColor: 'rgba(45, 226, 127, 0.24)',
					tension: 0.28,
					fill: true,
					pointRadius: 3,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					beginAtZero: true,
				},
			},
		},
	});
}

function renderMonthlyChart() {
	const source = appState.data.charts.monthly_sales;
	createOrReplaceChart('monthlySalesChart', 'monthlySalesChart', {
		type: 'bar',
		data: {
			labels: source.labels,
			datasets: [
				{
					label: 'Volume acumulado por mes',
					data: source.values,
					backgroundColor: '#1cc86e',
					borderRadius: 8,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					beginAtZero: true,
				},
			},
		},
	});
}

function renderStateChart() {
	const rows = filteredStates();
	createOrReplaceChart('stateStationsChart', 'stateStationsChart', {
		type: 'bar',
		data: {
			labels: rows.map((row) => row.estado),
			datasets: [
				{
					label: 'Quantidade de estacoes',
					data: rows.map((row) => row.stations),
					backgroundColor: '#0fa95b',
					borderRadius: 8,
				},
				{
					label: 'Fast DC (%)',
					data: rows.map((row) => row.fast_dc_rate),
					backgroundColor: '#82f8b4',
					borderRadius: 8,
					yAxisID: 'y1',
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					beginAtZero: true,
					position: 'left',
				},
				y1: {
					beginAtZero: true,
					max: 100,
					position: 'right',
					grid: {
						drawOnChartArea: false,
					},
				},
			},
		},
	});
}

function renderContentOnly() {
	renderSummary();
	renderKpis();
	renderLists();
	renderTopModels();
	renderTopStates();
}

function renderChartsOnly() {
	renderManufacturerChart();
	renderYearlyChart();
	renderMonthlyChart();
	renderStateChart();
}

function renderAll() {
	renderContentOnly();
	renderChartsOnly();
}

function scheduleChartHydration(maxAttempts = 24) {
	const attempt = (remaining) => {
		if (!appState.data) {
			return;
		}

		if (setChartDefaults()) {
			renderChartsOnly();
			return;
		}

		if (remaining <= 0) {
			return;
		}

		window.setTimeout(() => attempt(remaining - 1), 250);
	};

	if ('requestIdleCallback' in window) {
		window.requestIdleCallback(() => attempt(maxAttempts), { timeout: 1000 });
		return;
	}

	window.setTimeout(() => attempt(maxAttempts), 0);
}

function bindControls() {
	elementById('manufacturerChartType')?.addEventListener('change', () => {
		if (setChartDefaults()) {
			renderManufacturerChart();
			return;
		}

		scheduleChartHydration(12);
	});

	elementById('modelLimit')?.addEventListener('input', () => {
		renderTopModels();
	});

	elementById('stateFastFilter')?.addEventListener('input', () => {
		renderTopStates();
		if (setChartDefaults()) {
			renderStateChart();
		}
	});
}

function showFatalError(error) {
	const summaryNode = elementById('summaryText');
	if (summaryNode) {
		summaryNode.textContent = `Erro ao carregar dashboard: ${error}`;
	}
}

async function bootstrap() {
	try {
		const embeddedNode = elementById('analysisData');
		if (embeddedNode?.textContent) {
			try {
				appState.data = JSON.parse(embeddedNode.textContent);
			} catch (embeddedError) {
				console.warn('Falha ao ler dados embutidos. Tentando analysis.json...', embeddedError);
			}
		}

		if (!appState.data) {
			const response = await fetch('./analysis.json', { cache: 'no-store' });
			if (!response.ok) {
				throw new Error(`Falha HTTP ${response.status}`);
			}

			appState.data = await response.json();
		}

		bindControls();
		renderContentOnly();
		scheduleChartHydration();
	} catch (error) {
		showFatalError(error instanceof Error ? error.message : String(error));
	}
}

window.addEventListener('DOMContentLoaded', bootstrap);
