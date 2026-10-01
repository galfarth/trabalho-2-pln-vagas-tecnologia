#!/usr/bin/env python3
"""Valida os arquivos do dataset do Trabalho 2 de PLN."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "dados" / "raw"
PROCESSED_DIR = ROOT / "dados" / "processed"

def ultimo_arquivo(pasta: Path, padroes: tuple[str, ...]) -> Path | None:
    candidatos: list[Path] = []
    for padrao in padroes:
        candidatos.extend(pasta.glob(padrao))
    candidatos = [p for p in candidatos if p.is_file()]
    return max(candidatos, key=lambda p: p.stat().st_mtime) if candidatos else None

def contar_jsonl(caminho: Path) -> int:
    total = 0
    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                json.loads(linha)
                total += 1
    return total

def main() -> int:
    raw = ultimo_arquivo(RAW_DIR, ("vagas_*.jsonl", "vagas_raw_*.jsonl", "*.jsonl"))
    csv = ultimo_arquivo(PROCESSED_DIR, ("vagas_processadas_*.csv", "*.csv"))
    if raw is None or csv is None:
        print("Dataset incompleto.")
        return 2
    bruto = contar_jsonl(raw)
    df = pd.read_csv(csv)
    ids_unicos = df["id_vaga"].nunique() if "id_vaga" in df.columns else None
    descricoes_vazias = int(df["descricao"].fillna("").astype(str).str.strip().eq("").sum()) if "descricao" in df.columns else None
    print("Validação do dataset")
    print(f"JSONL: {raw.relative_to(ROOT)}")
    print(f"CSV: {csv.relative_to(ROOT)}")
    print(f"Registros brutos: {bruto}")
    print(f"Vagas processadas: {len(df)}")
    print(f"IDs únicos no CSV: {ids_unicos}")
    print(f"Descrições vazias no CSV: {descricoes_vazias}")
    esperado = (bruto == 600 and len(df) == 568 and ids_unicos == 568 and descricoes_vazias == 0)
    if esperado:
        print("\nOK: os principais indicadores correspondem à execução documentada no relatório.")
        return 0
    print("\nATENÇÃO: os indicadores diferem da execução de 15/09/2026.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
