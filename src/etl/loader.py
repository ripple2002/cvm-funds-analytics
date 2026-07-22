from pathlib import Path
import psycopg


DDL_SCHEMA = """
DROP TABLE IF EXISTS cadastro_geral CASCADE;

CREATE TABLE cadastro_geral (
    tp_fundo TEXT,
    cnpj_fundo TEXT,
    denom_social TEXT,
    dt_reg TEXT,
    dt_const TEXT,
    cd_cvm TEXT,
    dt_cancel TEXT,
    sit TEXT,
    dt_ini_sit TEXT,
    dt_ini_ativ TEXT,
    dt_ini_exerc TEXT,
    dt_fim_exerc TEXT,
    classe TEXT,
    dt_ini_classe TEXT,
    rentab_fundo TEXT,
    condom TEXT,
    fundo_cotas TEXT,
    fundo_exclusivo TEXT,
    trib_lprazo TEXT,
    publico_alvo TEXT,
    entid_invest TEXT,
    taxa_perfm TEXT,
    inf_taxa_perfm TEXT,
    taxa_adm TEXT,
    inf_taxa_adm TEXT,
    vl_patrim_liq TEXT,
    dt_patrim_liq TEXT,
    diretor TEXT,
    cnpj_admin TEXT,
    admin TEXT,
    pf_pj_gestor TEXT,
    cpf_cnpj_gestor TEXT,
    gestor TEXT,
    cnpj_auditor TEXT,
    auditor TEXT,
    cnpj_custodiante TEXT,
    custodiante TEXT,
    cnpj_controlador TEXT,
    controlador TEXT,
    invest_cempr_exter TEXT,
    classe_anbima TEXT
);
CREATE INDEX IF NOT EXISTS idx_cad_cnpj ON cadastro_geral (cnpj_fundo);


DROP TABLE IF EXISTS informe_diario CASCADE;

CREATE TABLE informe_diario (
    tp_fundo_classe TEXT,
    cnpj_fundo_classe TEXT,
    id_subclasse TEXT,
    dt_comptc DATE,
    vl_total NUMERIC(18, 2),
    vl_quota NUMERIC(18, 8),
    vl_patrim_liq NUMERIC(18, 2),
    captc_dia NUMERIC(18, 2),
    resg_dia NUMERIC(18, 2),
    nr_cotst INTEGER
);

CREATE INDEX IF NOT EXISTS idx_informe_data_pl 
ON informe_diario (dt_comptc DESC, vl_patrim_liq DESC);

CREATE INDEX IF NOT EXISTS idx_informe_cnpj 
ON informe_diario (cnpj_fundo_classe);
"""


def init_db(config: dict) -> None:
    with psycopg.connect(**config) as conn, conn.cursor() as cur:
        cur.execute(DDL_SCHEMA)


def load_cadastro(file_path: Path, config: dict) -> None:
    with psycopg.connect(**config) as conn, conn.cursor() as cur, open(file_path, "rb") as f:
        cur.execute("TRUNCATE TABLE cadastro_geral CASCADE;")
        
        query = r"COPY cadastro_geral FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ';', ENCODING 'LATIN1', QUOTE E'\b')"
        
        with cur.copy(query) as copy:
            while chunk := f.read(65536):
                copy.write(chunk)


def load_informe_mensal(file_path: Path, ano_mes: str, config: dict) -> None:
    with psycopg.connect(**config) as conn, conn.cursor() as cur, open(file_path, "rb") as f:
        cur.execute("DELETE FROM informe_diario WHERE TO_CHAR(dt_comptc, 'YYYYMM') = %s;", (ano_mes,))
        
        with cur.copy("COPY informe_diario FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ';', ENCODING 'LATIN1')") as copy:
            while chunk := f.read(65536):
                copy.write(chunk)