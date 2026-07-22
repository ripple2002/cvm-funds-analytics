from pathlib import Path
import numpy as np
import pandas as pd


def transform_cad_fi(file_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path, sep=";", encoding="iso-8859-1", dtype=str
    )
    df.columns = df.columns.str.lower().str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

    colunas_cnpj = [col for col in df.columns if "cnpj" in col]
    for col in colunas_cnpj:
        df[col] = df[col].str.replace(r"[^\d]", "", regex=True)

    if "cnpj_fundo" in df.columns:
        df = df.drop_duplicates(subset=["cnpj_fundo"], keep="last")

    df = df.replace({np.nan: None, "": None})
    return df


def transform_informe_diario(file_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path, sep=";", encoding="iso-8859-1", dtype=str
    )
    df.columns = df.columns.str.lower().str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

    if "cnpj_fundo_classe" in df.columns:
        df["cnpj_fundo_classe"] = df["cnpj_fundo_classe"].str.replace(
            r"[^\d]", "", regex=True
        )

    if "cnpj_fundo_classe" in df.columns and "dt_comptc" in df.columns:
        df = df.drop_duplicates(subset=["cnpj_fundo_classe", "dt_comptc"], keep="last")

    df = df.replace({np.nan: None, "": None})
    return df