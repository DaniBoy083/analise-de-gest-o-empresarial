declare const Chart: any;

interface TopModel {
	modelo: string;
	fabricante: string;
	quantidade: number;
	market_share: number;
}

interface TopState {
	estado: string;
	stations: number;
	cities: number;
	fast_dc_rate: number;
	avg_power_kw: number;
	attractiveness_score: number;
}

interface ChartData {
	labels: string[];
	values: number[];
}

interface AnalysisData {
	executive_summary: string;
	meta: {
		dataset_origin: string;
		generated_at: string;
	};
	kpis: {
		total_units: number;
		total_models: number;
		total_manufacturers: number;
		top_manufacturer: string;
		top_manufacturer_share: number;
		growth_cagr: number;
		recommended_state: string;
	};
	insights: string[];
	recommendations: string[];
	tables: {
		top_models: TopModel[];
		top_states: TopState[];
	};
	charts: {
		manufacturer_share: ChartData;
		yearly_sales: ChartData;
		monthly_sales: ChartData;
	};
}

interface AppState {
	data: AnalysisData | null;
	charts: Record<string, any>;
	controlsBound: boolean;
	initialized: boolean;
	chartsHydrated: boolean;
	selectedState: string | null;
}

const appState: AppState = {
	data: null,
	charts: {},
	controlsBound: false,
	initialized: false,
	chartsHydrated: false,
	selectedState: null,
};

const integerFormatter = new Intl.NumberFormat('pt-BR');
const decimalFormatter = new Intl.NumberFormat('pt-BR', {
	minimumFractionDigits: 1,
	maximumFractionDigits: 1,
});

function setChartDefaults(): boolean {
	if (typeof Chart === 'undefined') {
		return false;
	}

	Chart.defaults.color = '#a4ebbf';
	Chart.defaults.borderColor = 'rgba(45, 226, 127, 0.24)';
	return true;
}

function elementById(id: string): HTMLElement | null {
	return document.getElementById(id);
}

function inputById(id: string): HTMLInputElement | null {
	return document.getElementById(id) as HTMLInputElement | null;
}

function selectById(id: string): HTMLSelectElement | null {
	return document.getElementById(id) as HTMLSelectElement | null;
}

function safeText(id: string, value: string): void {
	const node = elementById(id);
	if (node) {
		node.textContent = value;
	}
}

function escapeHtml(value: string | number): string {
	return String(value)
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#039;');
}

function chartOrNull(key: string): any | null {
	return appState.charts[key] ?? null;
}

function createOrReplaceChart(key: string, canvasId: string, config: object): void {
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

function renderSummary(): void {
	const data = appState.data;
	if (!data) return;
	safeText('summaryText', data.executive_summary);
	safeText('datasetSource', `Fonte: ${data.meta.dataset_origin}`);
	safeText(
		'generatedAt',
		`Gerado em: ${new Date(data.meta.generated_at).toLocaleString('pt-BR')}`
	);
}

function renderKpis(): void {
	const kpis = appState.data?.kpis;
	if (!kpis) return;
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

function renderLists(): void {
	const insightsNode = elementById('insightsList');
	const recommendationsNode = elementById('recommendationsList');

	if (insightsNode && appState.data) {
		insightsNode.innerHTML = appState.data.insights
			.map((item: string) => `<li>${escapeHtml(item)}</li>`)
			.join('');
	}

	if (recommendationsNode && appState.data) {
		recommendationsNode.innerHTML = appState.data.recommendations
			.map((item: string) => `<li>${escapeHtml(item)}</li>`)
			.join('');
	}
}

function renderTopModels(): void {
	const tableBody = elementById('topModelsTable');
	const modelLimit = Number(inputById('modelLimit')?.value || 12);
	safeText('modelLimitValue', String(modelLimit));

	if (!tableBody || !appState.data) {
		return;
	}

	const rows = appState.data.tables.top_models.slice(0, modelLimit);
	tableBody.innerHTML = rows
		.map(
			(row: TopModel) =>
				`<tr>\n`
				+ `<td data-label="Modelo">${escapeHtml(row.modelo)}</td>\n`
				+ `<td data-label="Fabricante">${escapeHtml(row.fabricante)}</td>\n`
				+ `<td data-label="Quantidade">${integerFormatter.format(row.quantidade)}</td>\n`
				+ `<td data-label="Market Share (%)">${decimalFormatter.format(row.market_share)}</td>\n`
				+ `</tr>`
		)
		.join('');
}

function selectedFastFilter(): number {
	return Number(selectById('stateFastFilter')?.value || inputById('stateFastFilter')?.value || 0);
}

function filteredStates(): TopState[] {
	const threshold = selectedFastFilter();
	return appState.data?.tables.top_states.filter((row: TopState) => row.fast_dc_rate >= threshold) ?? [];
}

function renderTopStates(): void {
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
			(row: TopState) =>
				`<tr>\n`
				+ `<td data-label="Estado">${escapeHtml(row.estado)}</td>\n`
				+ `<td data-label="Estacoes">${integerFormatter.format(row.stations)}</td>\n`
				+ `<td data-label="Cidades">${integerFormatter.format(row.cities)}</td>\n`
				+ `<td data-label="Fast DC (%)">${decimalFormatter.format(row.fast_dc_rate)}</td>\n`
				+ `<td data-label="Potencia Media (kW)">${decimalFormatter.format(row.avg_power_kw)}</td>\n`
				+ `<td data-label="Score">${decimalFormatter.format(row.attractiveness_score)}</td>\n`
				+ `</tr>`
		)
		.join('');
}

function renderManufacturerChart(): void {
	const chartType = selectById('manufacturerChartType')?.value || 'doughnut';
	const source = appState.data?.charts.manufacturer_share;
	if (!source) return;
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
						label(context: any) {
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

function renderYearlyChart(): void {
	const source = appState.data?.charts.yearly_sales;
	if (!source) return;
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
						title(context: any[]) {
							return `Ano ${context[0].label}`;
						},
						label(context: any) {
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

function renderMonthlyChart(): void {
	const source = appState.data?.charts.monthly_sales;
	if (!source) return;
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

function renderStateChart(): void {
	const rows = filteredStates();
	createOrReplaceChart('stateStationsChart', 'stateStationsChart', {
		type: 'bar',
		data: {
			labels: rows.map((row: TopState) => row.estado),
			datasets: [
				{
					label: 'Quantidade de estacoes',
					data: rows.map((row: TopState) => row.stations),
					backgroundColor: '#0fa95b',
					borderRadius: 8,
				},
				{
					label: 'Fast DC (%)',
					data: rows.map((row: TopState) => row.fast_dc_rate),
					backgroundColor: '#82f8b4',
					borderRadius: 8,
					yAxisID: 'y1',
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			onClick(event: any, elements: any[], chart: any) {
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
						title(context: any[]) {
							return String(context[0].label);
						},
						label(context: any) {
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

function downloadFile(filename: string, content: string, mimeType: string): void {
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

function exportModelsCsv(): void {
	if (!appState.data) return;
	const header = ['Modelo', 'Fabricante', 'Quantidade', 'Market Share (%)'];
	const rows = appState.data.tables.top_models.slice(0, Number(inputById('modelLimit')?.value || 12));
	const csv = [header.join(';'), ...rows.map((row: TopModel) => [row.modelo, row.fabricante, row.quantidade, row.market_share].join(';'))].join('\n');
	downloadFile('top_modelos.csv', csv, 'text/csv;charset=utf-8;');
}

function exportStatesJson(): void {
	const rows = filteredStates();
	downloadFile('top_estados.json', JSON.stringify(rows, null, 2), 'application/json');
}

function clearStateSelection(): void {
	appState.selectedState = null;
	renderStateDetail();
}

function renderStateDetail(): void {
	const panel = elementById('stateDetailPanel');
	if (!panel) {
		return;
	}

	if (!appState.selectedState) {
		panel.innerHTML = '<p>Selecione uma barra no gráfico de estados para ver métricas detalhadas.</p>';
		return;
	}

	const row = appState.data?.tables.top_states.find((item: TopState) => item.estado === appState.selectedState);
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

function renderContentOnly(): void {
	renderSummary();
	renderKpis();
	renderLists();
	renderTopModels();
	renderTopStates();
}

function renderChartsOnly(): void {
	if (appState.chartsHydrated) {
		renderManufacturerChart();
		renderStateDetail();
		return;
	}

	renderManufacturerChart();
	renderYearlyChart();
	renderMonthlyChart();
	renderStateChart();
	renderStateDetail();

	appState.chartsHydrated = true;
}

function renderAll(): void {
	renderContentOnly();
	renderChartsOnly();
}

function scheduleChartHydration(maxAttempts = 24): void {
	const requiredChartKeys = ['manufacturerChart', 'yearlySalesChart', 'monthlySalesChart', 'stateStationsChart'];

	const attempt = (remaining: number): void => {
		if (!appState.data) {
			return;
		}

		if (!setChartDefaults()) {
			if (remaining <= 0) {
				return;
			}
			window.setTimeout(() => attempt(remaining - 1), 250);
			return;
		}

		renderChartsOnly();

		const allCreated = requiredChartKeys.every((k: string) => !!appState.charts[k]);
		if (!allCreated && remaining > 0) {
			window.setTimeout(() => attempt(remaining - 1), 250);
			return;
		}
	};

	if ('requestIdleCallback' in window) {
		(window as any).requestIdleCallback(() => attempt(maxAttempts), { timeout: 1000 });
		return;
	}

	globalThis.setTimeout(() => attempt(maxAttempts), 0);
}

function bindControls(): void {
	if (appState.controlsBound) {
		return;
	}

	const manufacturerSelect = selectById('manufacturerChartType');
	manufacturerSelect?.addEventListener('change', () => {
		if (setChartDefaults()) {
			renderManufacturerChart();
			return;
		}

		if (appState.chartsHydrated) {
			renderManufacturerChart();
			return;
		}

		scheduleChartHydration(12);
	});

	const modelLimitInput = inputById('modelLimit');
	modelLimitInput?.addEventListener('input', () => {
		renderTopModels();
		const value = Number(modelLimitInput?.value || 0);
		safeText('modelLimitValue', String(value));
	});

	const stateFilterInput = inputById('stateFastFilter');
	stateFilterInput?.addEventListener('input', () => {
		renderTopStates();
		if (setChartDefaults()) {
			if (appState.chartsHydrated) {
				renderStateChart();
			} else {
				scheduleChartHydration(8);
			}
		}
		const val = Number(stateFilterInput?.value || 0);
		safeText('stateFastFilterValue', `${val}%`);
	});

	elementById('exportModelsCsv')?.addEventListener('click', exportModelsCsv);
	elementById('exportStatesJson')?.addEventListener('click', exportStatesJson);
	elementById('clearStateSelection')?.addEventListener('click', () => {
		clearStateSelection();
		if (setChartDefaults()) {
			if (appState.chartsHydrated) {
				renderStateChart();
			} else {
				scheduleChartHydration(8);
			}
		}
	});

	appState.controlsBound = true;
}

function showFatalError(error: string): void {
	const summaryNode = elementById('summaryText');
	if (summaryNode) {
		summaryNode.textContent = `Erro ao carregar dashboard: ${error}`;
	}
}

async function bootstrap(): Promise<void> {
	try {
		if (appState.initialized) {
			return;
		}
		const embeddedNode = elementById('analysisData');
		if (embeddedNode?.textContent) {
			try {
				appState.data = JSON.parse(embeddedNode.textContent) as AnalysisData;
			} catch (embeddedError) {
				console.warn('Falha ao ler dados embutidos. Tentando analysis.json...', embeddedError);
			}
		}

		if (!appState.data) {
			const response = await fetch('./analysis.json', { cache: 'no-store' });
			if (!response.ok) {
				throw new Error(`Falha HTTP ${response.status}`);
			}

			appState.data = await response.json() as AnalysisData;
		}

		bindControls();

		const manufacturerSelect = selectById('manufacturerChartType');
		if (manufacturerSelect) {
			manufacturerSelect.innerHTML = `
				<option value="doughnut">Rosca</option>
				<option value="bar">Barra</option>
				<option value="line">Linha</option>
			`;
		}

		const modelLimitInput = inputById('modelLimit');
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

		const stateFilterInput = inputById('stateFastFilter');
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