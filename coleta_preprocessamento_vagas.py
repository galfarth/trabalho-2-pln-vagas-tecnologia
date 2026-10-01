"""Coleta e pre-processamento de vagas de tecnologia pela API Adzuna.

Uso:
    pip install requests pandas
    export ADZUNA_APP_ID="seu_app_id"
    export ADZUNA_APP_KEY="sua_app_key"
    python coleta_preprocessamento_vagas.py --paginas 2 --resultados 50

Os arquivos sao gravados em dados/raw e dados/processed. O script evita
duplicidades, preserva o texto original e cria representacoes normalizadas,
tokenizadas e com stemming. A lematizacao e opcional quando spaCy e o modelo
pt_core_news_sm estiverem instalados.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

API_URL = "https://api.adzuna.com/v1/api/jobs/br/search/{pagina}"
CONSULTAS = [
    "desenvolvedor", "analista de dados", "cientista de dados",
    "devops", "seguranca da informacao", "suporte de tecnologia",
]

STOPWORDS_PT = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo",
    "as", "ate", "com", "como", "da", "das", "de", "dela", "dele", "do",
    "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era", "essa",
    "essas", "esse", "esses", "esta", "estas", "este", "estes", "eu", "foi",
    "for", "ha", "isso", "isto", "ja", "mais", "mas", "me", "mesmo", "meu",
    "minha", "muito", "na", "nas", "nao", "no", "nos", "nossa", "nosso",
    "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "que",
    "se", "sem", "ser", "seu", "sua", "tambem", "tem", "um", "uma", "voce",
}

def obter_credenciais() -> tuple[str, str]:
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    if not app_id or not app_key:
        raise RuntimeError(
            "Defina ADZUNA_APP_ID e ADZUNA_APP_KEY. Cadastro: "
            "https://developer.adzuna.com/"
        )
    return app_id, app_key

def coletar_pagina(
    sessao: requests.Session,
    consulta: str,
    pagina: int,
    resultados: int,
    app_id: str,
    app_key: str,
) -> list[dict[str, Any]]:
    parametros = {
        "app_id": app_id,
        "app_key": app_key,
        "what": consulta,
        "results_per_page": resultados,
        "content-type": "application/json",
        "sort_by": "date",
    }
    resposta = sessao.get(
        API_URL.format(pagina=pagina), params=parametros, timeout=30
    )
    resposta.raise_for_status()
    return resposta.json().get("results", [])

def achatar_vaga(vaga: dict[str, Any], consulta: str) -> dict[str, Any]:
    local = vaga.get("location") or {}
    empresa = vaga.get("company") or {}
    categoria = vaga.get("category") or {}
    texto_id = "|".join(
        str(vaga.get(campo, "")) for campo in ("id", "title", "created", "redirect_url")
    )
    return {
        "id_vaga": vaga.get("id") or hashlib.sha256(texto_id.encode()).hexdigest()[:20],
        "consulta_origem": consulta,
        "titulo": vaga.get("title", ""),
        "descricao": vaga.get("description", ""),
        "empresa": empresa.get("display_name", ""),
        "localizacao": local.get("display_name", ""),
        "categoria": categoria.get("label", ""),
        "salario_minimo": vaga.get("salary_min"),
        "salario_maximo": vaga.get("salary_max"),
        "tipo_contrato": vaga.get("contract_type", ""),
        "data_publicacao": vaga.get("created", ""),
        "url": vaga.get("redirect_url", ""),
        "coletado_em_utc": datetime.now(timezone.utc).isoformat(),
    }

def remover_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = re.sub(r"https?://\S+|www\.\S+", " ", texto)
    texto = re.sub(r"\S+@\S+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def normalizar(texto: str) -> str:
    texto = remover_html(texto).lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9+#.\s-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def tokenizar(texto: str) -> list[str]:
    return re.findall(r"(?:c\+\+|c#|\.net|[a-z0-9]+(?:[.-][a-z0-9]+)*)", texto)

def filtrar_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS_PT and (len(t) > 1 or t in {"c", "r"})]

def aplicar_stemming(tokens: list[str]) -> list[str]:
    try:
        from nltk.stem import RSLPStemmer
        stemmer = RSLPStemmer()
        return [stemmer.stem(t) for t in tokens]
    except (ImportError, LookupError):
        return tokens

def aplicar_lematizacao(texto: str) -> str:
    try:
        import spacy
        nlp = spacy.load("pt_core_news_sm", disable=["parser", "ner"])
        return " ".join(token.lemma_ for token in nlp(texto) if not token.is_space)
    except (ImportError, OSError):
        return ""

def preprocessar(df: pd.DataFrame, usar_lematizacao: bool) -> pd.DataFrame:
    df = df.copy()
    df["texto_original"] = (
        df["titulo"].fillna("").astype(str) + ". " + df["descricao"].fillna("").astype(str)
    )
    df["texto_sem_ruidos"] = df["texto_original"].map(remover_html)
    df["texto_normalizado"] = df["texto_original"].map(normalizar)
    df["tokens"] = df["texto_normalizado"].map(tokenizar)
    df["tokens_sem_stopwords"] = df["tokens"].map(filtrar_tokens)
    df["texto_processado"] = df["tokens_sem_stopwords"].map(" ".join)
    df["stems"] = df["tokens_sem_stopwords"].map(aplicar_stemming).map(" ".join)
    if usar_lematizacao:
        df["lemas"] = df["texto_processado"].map(aplicar_lematizacao)
    return df

def salvar_jsonl(registros: list[dict[str, Any]], caminho: Path) -> None:
    with caminho.open("w", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

def executar(args: argparse.Namespace) -> None:
    app_id, app_key = obter_credenciais()
    raw_dir = Path(args.saida) / "raw"
    processed_dir = Path(args.saida) / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    registros: list[dict[str, Any]] = []
    with requests.Session() as sessao:
        for consulta in CONSULTAS:
            for pagina in range(1, args.paginas + 1):
                vagas = coletar_pagina(
                    sessao, consulta, pagina, args.resultados, app_id, app_key
                )
                registros.extend(achatar_vaga(vaga, consulta) for vaga in vagas)
                time.sleep(args.intervalo)
    if not registros:
        raise RuntimeError("A API nao retornou vagas para as consultas configuradas.")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    salvar_jsonl(registros, raw_dir / f"vagas_{timestamp}.jsonl")
    df = pd.DataFrame(registros)
    df = df.drop_duplicates(subset=["id_vaga"], keep="first")
    df = df[df["descricao"].fillna("").str.strip().ne("")]
    processado = preprocessar(df, args.lematizar)
    processado.to_csv(
        processed_dir / f"vagas_processadas_{timestamp}.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Concluido: {len(processado)} vagas unicas processadas.")

def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paginas", type=int, default=2)
    parser.add_argument("--resultados", type=int, default=50)
    parser.add_argument("--intervalo", type=float, default=1.0)
    parser.add_argument("--saida", default="dados")
    parser.add_argument("--lematizar", action="store_true")
    args, _argumentos_do_ambiente = parser.parse_known_args()
    return args

if __name__ == "__main__":
    executar(argumentos())
