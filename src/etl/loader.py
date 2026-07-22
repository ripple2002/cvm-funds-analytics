from pathlib import Path

import psycopg

from .transformer import (
    transform_registro_classe,
    transform_informe_diario,
)


DDL_SCHEMA = """
DROP TABLE IF EXISTS informe_diario CASCADE;
DROP TABLE IF EXISTS classe CASCADE;

CREATE TABLE classe (
    cnpj_classe VARCHAR(14) PRIMARY KEY,
    id_registro_fundo TEXT,
    id_registro_classe TEXT,
    codigo_cvm TEXT,
    denominacao_social TEXT,
    situacao TEXT,
    classificacao TEXT,
    classificacao_anbima TEXT,
    tributacao_longo_prazo TEXT,
    publico_alvo TEXT,
    exclusivo TEXT,
    cnpj_custodiante VARCHAR(14),
    custodiante TEXT,
    cnpj_auditor VARCHAR(14),
    auditor TEXT
);

CREATE TABLE informe_diario (
    tp_fundo_classe TEXT,
    cnpj_fundo_classe VARCHAR(14)
        REFERENCES classe(cnpj_classe),
    id_subclasse TEXT,
    dt_comptc DATE,
    vl_total NUMERIC(18,2),
    vl_quota NUMERIC(18,8),
    vl_patrim_liq NUMERIC(18,2),
    captc_dia NUMERIC(18,2),
    resg_dia NUMERIC(18,2),
    nr_cotst INTEGER,
    PRIMARY KEY (
        cnpj_fundo_classe,
        dt_comptc
    )
);
"""


def init_db(config: dict) -> None:
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL_SCHEMA)


def load_classe(
    file_path: Path | str,
    config: dict,
) -> None:
    df_limpo = transform_registro_classe(file_path)

    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE classe CASCADE;")

            with cur.copy(
                "COPY classe FROM STDIN;"
            ) as copy:
                for row in df_limpo.itertuples(
                    index=False,
                    name=None,
                ):
                    copy.write_row(row)

    print(
        f"[OK] Cadastro: "
        f"{len(df_limpo)} classes carregadas."
    )


def load_informe_diario(
    file_path: Path | str,
    ano_mes: str,
    config: dict,
) -> None:
    df_limpo = transform_informe_diario(file_path)

    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cnpj_classe FROM classe;"
            )

            cnpjs_cadastrados = {
                row[0]
                for row in cur.fetchall()
            }

            mask_invalidos = ~df_limpo[
                "cnpj_fundo_classe"
            ].isin(cnpjs_cadastrados)

            registros_invalidos = df_limpo[
                mask_invalidos
            ]

            if not registros_invalidos.empty:
                cnpjs_invalidos = (
                    registros_invalidos[
                        "cnpj_fundo_classe"
                    ]
                    .drop_duplicates()
                    .tolist()
                )

                print(
                    f"[AVISO] {ano_mes}: "
                    f"{len(registros_invalidos)} registros ignorados, "
                    f"referentes a {len(cnpjs_invalidos)} CNPJs "
                    "não encontrados no cadastro."
                )

                print(
                    "[AVISO] Exemplos:",
                    cnpjs_invalidos[:10],
                )

            df_validos = df_limpo[
                ~mask_invalidos
            ]

            cur.execute(
                """
                DELETE FROM informe_diario
                WHERE TO_CHAR(dt_comptc, 'YYYYMM') = %s;
                """,
                (ano_mes,),
            )

            with cur.copy(
                "COPY informe_diario FROM STDIN;"
            ) as copy:
                for row in df_validos.itertuples(
                    index=False,
                    name=None,
                ):
                    copy.write_row(row)

    print(
        f"[OK] {ano_mes}: "
        f"{len(df_validos)} informes carregados."
    )