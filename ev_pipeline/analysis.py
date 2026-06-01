"""Camada de analise: transforma CSVs em payload para relatorio e dashboard."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from .config import DATASET_SLUG, KAGGLE_DOWNLOAD_URL, KAGGLE_URL
from .models import DatasetSources
from .states import normalize_state_name


def parse_market_share(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _prepare_carros(path: str) -> pd.DataFrame:
    carros = pd.read_csv(path)
    carros.columns = [str(column).strip() for column in carros.columns]
    carros["Quantidade"] = pd.to_numeric(carros["Quantidade"], errors="coerce").fillna(0)
    carros["MarketShare"] = parse_market_share(carros["MarketShare"])
    return carros


def _prepare_vendas(path: str) -> tuple[pd.DataFrame, list[str]]:
    vendas = pd.read_csv(path)
    vendas.columns = [str(column).strip() for column in vendas.columns]

    vendas["ano"] = pd.to_numeric(vendas["ano"], errors="coerce")
    vendas = vendas.dropna(subset=["ano"]).copy()
    vendas["ano"] = vendas["ano"].astype(int)

    value_columns = [column for column in vendas.columns if column != "ano"]
    for column in value_columns:
        vendas[column] = pd.to_numeric(vendas[column], errors="coerce")

    month_columns = [column for column in value_columns if column.lower() != "total"]

    if "Total" not in vendas.columns:
        vendas["Total"] = vendas[month_columns].sum(axis=1, skipna=True)
    else:
        missing_total = vendas["Total"].isna()
        if missing_total.any():
            vendas.loc[missing_total, "Total"] = vendas.loc[missing_total, month_columns].sum(
                axis=1,
                skipna=True,
            )

    vendas = vendas.sort_values("ano")
    return vendas, month_columns


def _prepare_estacoes(path: str) -> pd.DataFrame:
    estacoes = pd.read_csv(
        path,
        usecols=["id", "city", "country_code", "state_province", "power_kw", "is_fast_dc"],
        low_memory=False,
    )

    estacoes["country_code"] = estacoes["country_code"].astype(str).str.upper()
    estacoes["state_province"] = estacoes["state_province"].apply(normalize_state_name)
    estacoes["city"] = estacoes["city"].fillna("Nao informada").astype(str).str.strip()
    estacoes["power_kw"] = pd.to_numeric(estacoes["power_kw"], errors="coerce").fillna(0)
    estacoes["is_fast_dc"] = estacoes["is_fast_dc"].astype(str).str.lower().isin(
        ["true", "1", "yes"]
    )

    return estacoes


def _compute_yoy(values: list[int]) -> list[float | None]:
    yoy_growth: list[float | None] = []
    for index, current_value in enumerate(values):
        if index == 0:
            yoy_growth.append(None)
            continue

        previous_value = values[index - 1]
        if previous_value == 0:
            yoy_growth.append(None)
            continue

        yoy_growth.append(round(((current_value - previous_value) / previous_value) * 100, 2))

    return yoy_growth


def _compute_cagr(values: list[int]) -> float:
    if len(values) <= 1 or values[0] <= 0:
        return 0.0

    return round(((values[-1] / values[0]) ** (1 / (len(values) - 1)) - 1) * 100, 2)


def _build_state_rank(br_stations: pd.DataFrame) -> pd.DataFrame:
    br_known_states = br_stations[br_stations["state_province"] != "Nao informado"].copy()
    ranking_base = br_known_states if not br_known_states.empty else br_stations

    if ranking_base.empty:
        return pd.DataFrame(
            columns=[
                "state_province",
                "stations",
                "cities",
                "avg_power_kw",
                "fast_dc_rate",
                "attractiveness_score",
            ]
        )

    state_rank = ranking_base.groupby("state_province", as_index=False).agg(
        stations=("id", "count"),
        cities=("city", "nunique"),
        avg_power_kw=("power_kw", "mean"),
        fast_dc_rate=("is_fast_dc", "mean"),
    )

    state_rank["fast_dc_rate"] = state_rank["fast_dc_rate"].fillna(0) * 100
    state_rank["avg_power_kw"] = state_rank["avg_power_kw"].fillna(0)

    max_stations = max(float(state_rank["stations"].max()), 1.0)
    max_power = max(float(state_rank["avg_power_kw"].max()), 1.0)

    state_rank["attractiveness_score"] = (
        0.55 * (state_rank["stations"] / max_stations)
        + 0.25 * (state_rank["fast_dc_rate"] / 100)
        + 0.20 * (state_rank["avg_power_kw"] / max_power)
    ) * 100

    return state_rank.sort_values("attractiveness_score", ascending=False)


def build_analysis_payload(sources: DatasetSources, dataset_origin: str) -> dict:
    carros = _prepare_carros(str(sources.carros))
    vendas, month_columns = _prepare_vendas(str(sources.vendas))
    estacoes = _prepare_estacoes(str(sources.estacoes))

    total_units = int(carros["Quantidade"].sum())
    total_models = int(carros["Modelo"].nunique()) if not carros.empty else 0
    total_manufacturers = int(carros["Fabricante"].nunique()) if not carros.empty else 0

    manufacturer_totals = (
        carros.groupby("Fabricante", as_index=False)["Quantidade"]
        .sum()
        .sort_values("Quantidade", ascending=False)
    )

    if manufacturer_totals.empty:
        top_manufacturer = "Sem dados"
        top_manufacturer_units = 0
        top_manufacturer_share = 0.0
        top_5_share = 0.0
    else:
        top_manufacturer_row = manufacturer_totals.iloc[0]
        top_manufacturer = str(top_manufacturer_row["Fabricante"])
        top_manufacturer_units = int(top_manufacturer_row["Quantidade"])
        top_manufacturer_share = (
            round((top_manufacturer_units / total_units) * 100, 2) if total_units else 0.0
        )
        top_5_share = (
            round((manufacturer_totals.head(5)["Quantidade"].sum() / total_units) * 100, 2)
            if total_units
            else 0.0
        )

    if carros.empty:
        top_model_name = "Sem dados"
        top_model_units = 0
    else:
        top_model_row = carros.sort_values("Quantidade", ascending=False).iloc[0]
        top_model_name = str(top_model_row["Modelo"])
        top_model_units = int(top_model_row["Quantidade"])

    yearly = vendas[["ano", "Total"]].copy()
    yearly["Total"] = yearly["Total"].fillna(0)
    yearly_years = yearly["ano"].astype(str).tolist()
    yearly_values = yearly["Total"].round(0).astype(int).tolist()

    yoy_growth = _compute_yoy(yearly_values)
    growth_cagr = _compute_cagr(yearly_values) if yearly_values else 0.0

    monthly_totals = vendas[month_columns].sum(axis=0, skipna=True)
    month_labels = [str(month) for month in month_columns]
    month_values = [int(round(float(monthly_totals.get(month, 0)))) for month in month_columns]

    if month_values:
        max_month_index = month_values.index(max(month_values))
        best_month = month_labels[max_month_index]
        best_month_units = month_values[max_month_index]
    else:
        best_month = "N/A"
        best_month_units = 0

    br_stations = estacoes[estacoes["country_code"] == "BR"].copy()
    state_rank = _build_state_rank(br_stations)

    recommended_state = (
        str(state_rank.iloc[0]["state_province"]) if not state_rank.empty else "Sem dados"
    )
    brazil_station_count = int(len(br_stations))

    top_models = (
        carros.sort_values("Quantidade", ascending=False)
        .head(50)[["Modelo", "Fabricante", "Quantidade", "MarketShare"]]
        .copy()
    )
    top_models["MarketShare"] = top_models["MarketShare"].fillna(0)

    top_states = state_rank.head(20).copy()

    first_year = yearly_values[0] if yearly_values else 0
    last_year = yearly_values[-1] if yearly_values else 0

    insights = [
        (
            "A base soma "
            f"{total_units:,} unidades eletrificadas em circulacao, distribuida em "
            f"{total_models} modelos e {total_manufacturers} fabricantes."
        ),
        (
            f"{top_manufacturer} lidera com {top_manufacturer_share}% de market share "
            f"e {top_manufacturer_units:,} unidades."
        ),
        (
            f"A participacao conjunta dos 5 maiores fabricantes atinge {top_5_share}%, "
            "sinalizando concentracao relevante de mercado."
        ),
        (
            f"As vendas anuais evoluiram de {first_year:,} para {last_year:,} "
            f"unidades no periodo monitorado, com CAGR de {growth_cagr}% ao ano."
        ),
        (
            f"No recorte de infraestrutura, o Brasil tem {brazil_station_count} pontos "
            f"na base global e {recommended_state} aparece como estado com melhor score composto."
        ),
    ]

    recommendations = [
        (
            f"Priorizar a expansao em {recommended_state}, combinando postos de recarga rapida "
            "com acordos comerciais locais."
        ),
        (
            "Direcionar campanhas e parcerias para os fabricantes lideres, onde a demanda "
            "ja esta comprovada."
        ),
        (
            "Planejar capacidade para picos de demanda nos meses historicamente mais fortes, "
            "reduzindo risco operacional."
        ),
        (
            "Monitorar estados com alta quantidade de cidades e baixa densidade de estacoes "
            "como oportunidades de first-mover."
        ),
    ]

    executive_summary = (
        "O mercado brasileiro de eletrificados apresenta crescimento forte de vendas, "
        "com concentracao em poucos fabricantes e aceleracao de infraestrutura. "
        f"A recomendacao atual para investimento prioritario e {recommended_state}, "
        "considerando densidade de estacoes, potencia media e participacao de recarga rapida."
    )

    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset_slug": DATASET_SLUG,
            "dataset_origin": dataset_origin,
            "kaggle_url": KAGGLE_URL,
            "kaggle_download_url": KAGGLE_DOWNLOAD_URL,
            "source_files": {
                "carros_eletricos": str(sources.carros),
                "monitoramento_vendas": str(sources.vendas),
                "charging_stations": str(sources.estacoes),
            },
        },
        "executive_summary": executive_summary,
        "kpis": {
            "total_units": total_units,
            "total_models": total_models,
            "total_manufacturers": total_manufacturers,
            "top_manufacturer": top_manufacturer,
            "top_manufacturer_units": top_manufacturer_units,
            "top_manufacturer_share": top_manufacturer_share,
            "top_model": top_model_name,
            "top_model_units": top_model_units,
            "growth_cagr": growth_cagr,
            "best_month": best_month,
            "best_month_units": best_month_units,
            "br_station_count": brazil_station_count,
            "recommended_state": recommended_state,
        },
        "charts": {
            "manufacturer_share": {
                "labels": manufacturer_totals.head(8)["Fabricante"].tolist(),
                "values": manufacturer_totals.head(8)["Quantidade"].astype(int).tolist(),
            },
            "yearly_sales": {
                "labels": yearly_years,
                "values": yearly_values,
            },
            "yoy_growth": {
                "labels": yearly_years,
                "values": yoy_growth,
            },
            "monthly_sales": {
                "labels": month_labels,
                "values": month_values,
            },
            "state_stations": {
                "labels": top_states["state_province"].tolist(),
                "values": top_states["stations"].astype(int).tolist(),
                "fast_dc_rate": [
                    round(float(value), 2)
                    for value in top_states["fast_dc_rate"].tolist()
                ],
            },
        },
        "tables": {
            "top_models": [
                {
                    "modelo": str(row["Modelo"]),
                    "fabricante": str(row["Fabricante"]),
                    "quantidade": int(row["Quantidade"]),
                    "market_share": round(float(row["MarketShare"]), 2),
                }
                for _, row in top_models.iterrows()
            ],
            "top_states": [
                {
                    "estado": str(row["state_province"]),
                    "stations": int(row["stations"]),
                    "cities": int(row["cities"]),
                    "avg_power_kw": round(float(row["avg_power_kw"]), 2),
                    "fast_dc_rate": round(float(row["fast_dc_rate"]), 2),
                    "attractiveness_score": round(float(row["attractiveness_score"]), 2),
                }
                for _, row in top_states.iterrows()
            ],
        },
        "insights": insights,
        "recommendations": recommendations,
    }

    return payload
