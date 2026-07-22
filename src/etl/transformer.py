from pathlib import Path
import numpy as np
import pandas as pd

COLUNAS_CLASSE = [
    "cnpj_classe",
    "id_registro_fundo",
    "id_registro_classe",
    "codigo_cvm",
    "denominacao_social",
    "situacao",
    "classificacao",
    "classificacao_anbima",
    "tributacao_longo_prazo",
    "publico_alvo",
    "exclusivo",
    "cnpj_custodiante",
    "custodiante",
    "cnpj_auditor",
    "auditor",
]

def transform_registro_classe(file_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        sep=";",
        encoding="iso-8859-1",
        dtype=str,
    )

    df.columns = df.columns.str.lower().str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

    if "cnpj_classe" in df.columns:
        df["cnpj_classe"] = (
            df["cnpj_classe"]
            .str.replace(r"[^\d]", "", regex=True)
            .str.zfill(14)
        )

        df = df.drop_duplicates(
            subset=["cnpj_classe"],
            keep="last",
        )

    for col in ("cnpj_custodiante", "cnpj_auditor"):
        if col in df.columns:
            df[col] = (
                df[col]
                .str.replace(r"[^\d]", "", regex=True)
                .str.zfill(14)
            )

    df = df.replace({
        np.nan: None,
        "": None,
    })

    df = df[COLUNAS_CLASSE]

    return df



def transform_informe_diario(file_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        sep=";",
        encoding="iso-8859-1",
        dtype=str,
    )

    df.columns = df.columns.str.lower().str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

    if "cnpj_fundo_classe" in df.columns:
        df["cnpj_fundo_classe"] = (
            df["cnpj_fundo_classe"]
            .str.replace(r"[^\d]", "", regex=True)
            .str.zfill(14)
        )

    if (
        "cnpj_fundo_classe" in df.columns
        and "dt_comptc" in df.columns
    ):
        df = df.drop_duplicates(
            subset=["cnpj_fundo_classe", "dt_comptc"],
            keep="last",
        )

    df = df.replace({
        np.nan: None,
        "": None,
    })

    return df