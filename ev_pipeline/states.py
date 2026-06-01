"""Normalizacao de estados brasileiros para analise regional."""

import unicodedata
from typing import Any

import pandas as pd


def normalize_text_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return "".join(char for char in ascii_only.lower() if char.isalnum())


BR_STATES_BY_CODE = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapa",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Para",
    "PB": "Paraiba",
    "PR": "Parana",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondonia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "Sao Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

STATE_ALIASES: dict[str, str] = {
    "metropolitanregionofportoalegre": "Rio Grande do Sul",
    "toodejaneiro": "Rio de Janeiro",
    "naoinformado": "Nao informado",
    "notinformed": "Nao informado",
}

for uf_code, state_name in BR_STATES_BY_CODE.items():
    STATE_ALIASES[normalize_text_key(uf_code)] = state_name
    STATE_ALIASES[normalize_text_key(state_name)] = state_name


def normalize_state_name(raw_value: Any) -> str:
    if pd.isna(raw_value):
        return "Nao informado"

    value = str(raw_value).strip()
    key = normalize_text_key(value)
    if key in {"", "na", "nan", "none", "null", "naoinformado", "notinformed"}:
        return "Nao informado"

    if key in STATE_ALIASES:
        return STATE_ALIASES[key]

    return value.title()
