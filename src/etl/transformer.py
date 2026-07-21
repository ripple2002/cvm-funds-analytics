import pandas as pd


def transform_cad_fi(file_path):

    df = pd.read_csv(
        file_path, 
        sep=";", 
        encoding="iso-8859-1", 
        dtype=str
    )

    df.columns = df.columns.str.lower().str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

    return df




if __name__ == "__main__":
    path = "data/raw/cad_fi.csv"
    clean_df = transform_cad_fi(path)
    clean_df.to_csv("data/processed/cad_fi_limpo.csv", index=False, sep=";")
    