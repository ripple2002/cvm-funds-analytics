from pathlib import Path
import psycopg
from .transformer import transform_cad_fi, transform_informe_diario


DDL_SCHEMA = """

DROP TABLE IF EXISTS informe_diario CASCADE;
DROP TABLE IF EXISTS cadastro_geral CASCADE;

CREATE TABLE cadastro_geral (
    tp_fundo TEXT,
    cnpj_fundo VARCHAR(14) PRIMARY KEY,
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
    cnpj_admin VARCHAR(14),
    admin TEXT,
    pf_pj_gestor TEXT,
    cpf_cnpj_gestor TEXT,
    gestor TEXT,
    cnpj_auditor VARCHAR(14),
    auditor TEXT,
    cnpj_custodiante VARCHAR(14),
    custodiante TEXT,
    cnpj_controlador VARCHAR(14),
    controlador TEXT,
    invest_cempr_exter TEXT,
    classe_anbima TEXT
);

CREATE TABLE informe_diario (
    tp_fundo_classe TEXT,
    cnpj_fundo_classe VARCHAR(14), 
    id_subclasse TEXT,
    dt_comptc DATE,
    vl_total NUMERIC(18, 2),
    vl_quota NUMERIC(18, 8),
    vl_patrim_liq NUMERIC(18, 2),
    captc_dia NUMERIC(18, 2),
    resg_dia NUMERIC(18, 2),
    nr_cotst INTEGER,
    
    PRIMARY KEY (cnpj_fundo_classe, dt_comptc)
);

CREATE INDEX IF NOT EXISTS idx_informe_data_pl 
ON informe_diario (dt_comptc DESC, vl_patrim_liq DESC);
"""


def init_db(config: dict) -> None:
    with psycopg.connect(**config) as conn, conn.cursor() as cur:
        cur.execute(DDL_SCHEMA)


def load_cadastro(file_path: Path | str, config: dict) -> None:
    df_limpo = transform_cad_fi(file_path)

    with psycopg.connect(**config) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE cadastro_geral CASCADE;")

        with cur.copy("COPY cadastro_geral FROM STDIN;") as copy:
            for row in df_limpo.itertuples(index=False, name=None):
                copy.write_row(row)


def load_informe_diario(file_path: Path | str, ano_mes: str, config: dict) -> None:
    df_limpo = transform_informe_diario(file_path)
    
    with psycopg.connect(**config) as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM informe_diario WHERE TO_CHAR(dt_comptc, 'YYYYMM') = %s;",
            (ano_mes,),
        )

        with cur.copy("COPY informe_diario FROM STDIN;") as copy:
            for row in df_limpo.itertuples(index=False, name=None):
                copy.write_row(row)

