const appState = {
	data: null,
	charts: {},
	// evita dupla inicializacao / múltiplos listeners quando o script é re-executado
	controlsBound: false,
	initialized: false,
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
				tooltip: {
					callbacks: {
						label(context) {
							return `Unidades: ${integerFormatter.format(context.parsed)}`;
						},
					},
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
			plugins: {
				tooltip: {
					callbacks: {
						title(context) {
							return `Ano ${context[0].label}`;
						},
						label(context) {
							return `Unidades: ${integerFormatter.format(context.parsed.y)}`;
						},
					},
				},
			},
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
			onClick(event, elements, chart) {
				if (!elements.length) {
					return;
				}

				const element = elements[0];
				const stateLabel = chart.data.labels?.[element.index];
				if (stateLabel) {
					appState.selectedState = String(stateLabel);
					renderStateDetail();
				}
			},
			plugins: {
				tooltip: {
					callbacks: {
						title(context) {
							return String(context[0].label);
						},
						label(context) {
							return `${context.dataset.label}: ${integerFormatter.format(context.parsed.y)}`;
						},
					},
				},
			},
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

function downloadFile(filename, content, mimeType) {
	const blob = new Blob([content], { type: mimeType });
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = url;
	link.download = filename;
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	URL.revokeObjectURL(url);
}

function exportModelsCsv() {
	const header = ['Modelo', 'Fabricante', 'Quantidade', 'Market Share (%)'];
	const rows = appState.data.tables.top_models.slice(0, Number(elementById('modelLimit')?.value || 12));
	const csv = [header.join(';'), ...rows.map((row) => [row.modelo, row.fabricante, row.quantidade, row.market_share].join(';'))].join('\n');
	downloadFile('top_modelos.csv', csv, 'text/csv;charset=utf-8;');
}

function exportStatesJson() {
	const rows = filteredStates();
	downloadFile('top_estados.json', JSON.stringify(rows, null, 2), 'application/json');
}

function clearStateSelection() {
	appState.selectedState = null;
	renderStateDetail();
}

function renderStateDetail() {
	const panel = elementById('stateDetailPanel');
	if (!panel) {
		return;
	}

	if (!appState.selectedState) {
		panel.innerHTML = '<p>Selecione uma barra no gráfico de estados para ver métricas detalhadas.</p>';
		return;
	}

	const row = appState.data.tables.top_states.find((item) => item.estado === appState.selectedState);
	if (!row) {
		panel.innerHTML = `<p>O estado selecionado nao esta mais no filtro atual: ${escapeHtml(appState.selectedState)}.</p>`;
		return;
	}

	panel.innerHTML = `
		<p><strong>Estado:</strong> ${escapeHtml(row.estado)}</p>
		<p><strong>Estacoes:</strong> ${integerFormatter.format(row.stations)}</p>
		<p><strong>Cidades:</strong> ${integerFormatter.format(row.cities)}</p>
		<p><strong>Fast DC:</strong> ${decimalFormatter.format(row.fast_dc_rate)}%</p>
		<p><strong>Potencia Media:</strong> ${decimalFormatter.format(row.avg_power_kw)} kW</p>
		<p><strong>Score de Atratividade:</strong> ${decimalFormatter.format(row.attractiveness_score)}</p>
	`;
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
	renderStateDetail();
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
	if (appState.controlsBound) {
		return;
	}

	const manufacturerSelect = elementById('manufacturerChartType');
	manufacturerSelect?.addEventListener('change', () => {
		if (setChartDefaults()) {
			renderManufacturerChart();
			return;
		}

		scheduleChartHydration(12);
	});

	// Atualiza a tabela quando o slider de limite de modelos muda e atualiza o label
	const modelLimitInput = elementById('modelLimit') as HTMLInputElement | null;
	modelLimitInput?.addEventListener('input', () => {
		renderTopModels();
		const value = Number(modelLimitInput.value || 0);
		safeText('modelLimitValue', String(value));
	});

	const stateFilterInput = elementById('stateFastFilter') as HTMLInputElement | null;
	stateFilterInput?.addEventListener('input', () => {
		renderTopStates();
		if (setChartDefaults()) {
			renderStateChart();
		}
		const val = Number(stateFilterInput.value || 0);
		safeText('stateFastFilterValue', `${val}%`);
	});

	elementById('exportModelsCsv')?.addEventListener('click', exportModelsCsv);
	elementById('exportStatesJson')?.addEventListener('click', exportStatesJson);
	elementById('clearStateSelection')?.addEventListener('click', () => {
		clearStateSelection();
		if (setChartDefaults()) {
			renderStateChart();
		}
	});

	appState.controlsBound = true;
}

function showFatalError(error) {
	const summaryNode = elementById('summaryText');
	if (summaryNode) {
		summaryNode.textContent = `Erro ao carregar dashboard: ${error}`;
	}
}

async function bootstrap() {
	try {
		// evitar re-run se já inicializado (por ex. hot-reload ou execução repetida)
		if (appState.initialized) {
			return;
		}
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

		// Ajustes dinâmicos dos controles: definir limites e rótulos em PT-BR
		// 1) manufacturerChartType: opções legíveis
		const manufacturerSelect = elementById('manufacturerChartType') as HTMLSelectElement | null;
		if (manufacturerSelect) {
			manufacturerSelect.innerHTML = `
				<option value="doughnut">Rosca</option>
				<option value="bar">Barra</option>
				<option value="line">Linha</option>
			`;
		}

		// 2) modelLimit: ajustar max para quantidade de modelos disponíveis
		const modelLimitInput = elementById('modelLimit') as HTMLInputElement | null;
		const modelLimitValueNode = elementById('modelLimitValue');
		const availableModels = appState.data?.tables?.top_models?.length || 0;
		if (modelLimitInput) {
			modelLimitInput.min = '1';
			modelLimitInput.max = String(Math.max(1, Math.min(50, availableModels)));
			if (!modelLimitInput.value) {
				modelLimitInput.value = String(Math.min(12, availableModels || 12));
			}
		}
		if (modelLimitValueNode) {
			modelLimitValueNode.textContent = String(modelLimitInput?.value || '0');
		}

		// 3) stateFastFilter: exibir em porcentagem e definir range 0-100
		const stateFilterInput = elementById('stateFastFilter') as HTMLInputElement | null;
		const stateFilterValueNode = elementById('stateFastFilterValue');
		if (stateFilterInput) {
			stateFilterInput.min = '0';
			stateFilterInput.max = '100';
			stateFilterInput.step = '1';
			if (!stateFilterInput.value) {
				stateFilterInput.value = '0';
			}
		}
		if (stateFilterValueNode) {
			stateFilterValueNode.textContent = `${stateFilterInput?.value || '0'}%`;
		}

		renderContentOnly();
		scheduleChartHydration();
		appState.initialized = true;
	} catch (error) {
		showFatalError(error instanceof Error ? error.message : String(error));
	}
}

window.addEventListener('DOMContentLoaded', bootstrap);
