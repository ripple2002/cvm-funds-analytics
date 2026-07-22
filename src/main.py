import os
from etl.extractor import download_cvm_file, get_cad_fi_url, get_inf_diario_url
from etl.loader import init_db, load_cadastro, load_informe_diario

def main():

    month_window = [
        ("2024", "04"),
        ("2024", "05"),
        ("2024", "06"),
    ]

    db_config = {
        "dbname": os.getenv("POSTGRES_DB", "cvm"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "1234"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }

    init_db(db_config)

    cad_path = download_cvm_file(get_cad_fi_url())
    load_cadastro(cad_path, db_config)

    for ano, mes in month_window:
        ano_mes = f"{ano}{mes}"
        inf_path = download_cvm_file(get_inf_diario_url(ano, mes))
        load_informe_diario(inf_path, ano_mes, db_config)

    print("ETL concluido")

if __name__ == "__main__":
    main()