import os
import re
from typing import Optional
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
import psycopg
from psycopg.rows import dict_row
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="CVM Funds Analytics API",
    version="1.0.0",
    description="API para consulta de dados cadastrais e informes diários de fundos da CVM."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
        "dbname": os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "cvm")),
        "user": os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres")),
        "password": os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "1234")),
        "port": int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
    }


def normalize_cnpj(cnpj: Optional[str]) -> Optional[str]:
    if not cnpj:
        return None
    return re.sub(r"\D", "", cnpj)


def get_db_connection():
    return psycopg.connect(row_factory=dict_row, **get_db_config())



@app.get("/funds", summary="Buscar fundos cadastrados")
def search_funds(
    q: Optional[str] = Query(None, description="Termo de busca para o nome do fundo (denom_social)"),
    cnpj: Optional[str] = Query(None, description="CNPJ exato do fundo"),
    limit: int = Query(20, le=100, description="Número máximo de registros")
):
    normalized_cnpj = normalize_cnpj(cnpj)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM classe WHERE 1=1"
            params = []
            
            if normalized_cnpj:
                query += " AND cnpj_classe = %s"
                params.append(normalized_cnpj)
            if q:
                query += " AND denominacao_social ILIKE %s"
                params.append(f"%{q}%")
                
            query += " LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            results = cur.fetchall()
            return {"total": len(results), "data": results}
        


@app.get("/funds/{cnpj}/reports", summary="Consultar informe diário de um fundo")
def get_fund_reports(
    cnpj: str,
    start_date: Optional[str] = Query(None, description="Data inicial (AAAA-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (AAAA-MM-DD)"),
    limit: int = Query(30, le=365, description="Limite de registros")
):
    normalized_cnpj = normalize_cnpj(cnpj)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT * FROM informe_diario 
                WHERE cnpj_fundo_classe = %s
            """
            params = [normalized_cnpj]
            
            if start_date:
                query += " AND dt_comptc >= %s"
                params.append(start_date)
            if end_date:
                query += " AND dt_comptc <= %s"
                params.append(end_date)
                
            query += " ORDER BY dt_comptc DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            if not results:
                raise HTTPException(status_code=404, detail="Nenhum informe encontrado para este CNPJ no período.")

            return {"cnpj": normalized_cnpj, "total": len(results), "data": results}
        


@app.get("/funds/{cnpj}/history")
def get_fund_history(
    cnpj: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(365, ge=1, le=1000),
):
    normalized_cnpj = normalize_cnpj(cnpj)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    dt_comptc,
                    vl_quota,
                    vl_patrim_liq,
                    captc_dia,
                    resg_dia,
                    nr_cotst
                FROM informe_diario
                WHERE cnpj_fundo_classe = %s
            """

            params = [normalized_cnpj]

            if start_date:
                query += " AND dt_comptc >= %s"
                params.append(start_date)

            if end_date:
                query += " AND dt_comptc <= %s"
                params.append(end_date)

            query += """
                ORDER BY dt_comptc ASC
                LIMIT %s
            """

            params.append(limit)

            cur.execute(query, params)
            results = cur.fetchall()

            if not results:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum histórico encontrado.",
                )

            data = []

            for row in results:
                data.append({
                    "date": row["dt_comptc"],
                    "quota": row["vl_quota"],
                    "net_asset_value": row["vl_patrim_liq"],
                    "subscriptions": row["captc_dia"],
                    "redemptions": row["resg_dia"],
                    "net_flow": (
                        (row["captc_dia"] or 0)
                        - (row["resg_dia"] or 0)
                    ),
                    "shareholders": row["nr_cotst"],
                })

            return {
                "cnpj": normalized_cnpj,
                "total": len(data),
                "data": data,
            }



@app.get("/funds/{cnpj}/summary")
def get_fund_summary(
    cnpj: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    normalized_cnpj = normalize_cnpj(cnpj)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    i.dt_comptc,
                    i.vl_quota,
                    i.vl_patrim_liq,
                    i.captc_dia,
                    i.resg_dia,
                    i.nr_cotst
                FROM informe_diario i
                WHERE i.cnpj_fundo_classe = %s
            """

            params = [normalized_cnpj]

            if start_date:
                query += " AND i.dt_comptc >= %s"
                params.append(start_date)

            if end_date:
                query += " AND i.dt_comptc <= %s"
                params.append(end_date)

            query += " ORDER BY i.dt_comptc ASC"

            cur.execute(query, params)
            reports = cur.fetchall()

            if not reports:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum informe encontrado.",
                )

            first = reports[0]
            latest = reports[-1]

            period_return = None

            if first["vl_quota"] and first["vl_quota"] != 0:
                period_return = (
                    latest["vl_quota"] / first["vl_quota"]
                ) - 1

            net_flow = sum(
                (row["captc_dia"] or 0) - (row["resg_dia"] or 0)
                for row in reports
            )

            return {
                "cnpj": normalized_cnpj,
                "period": {
                    "start": first["dt_comptc"],
                    "end": latest["dt_comptc"],
                },
                "latest": {
                    "quota": latest["vl_quota"],
                    "net_asset_value": latest["vl_patrim_liq"],
                    "shareholders": latest["nr_cotst"],
                },
                "indicators": {
                    "period_return": period_return,
                    "net_flow": net_flow,
                },
            }
        


@app.get("/analytics/ranking")
def get_funds_ranking(
    limit: int = Query(10, ge=1, le=100),
):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (i.cnpj_fundo_classe)
                    i.cnpj_fundo_classe AS cnpj,
                    c.denominacao_social,
                    i.dt_comptc,
                    i.vl_quota,
                    i.vl_patrim_liq,
                    i.nr_cotst
                FROM informe_diario i
                LEFT JOIN classe c
                    ON c.cnpj_classe = i.cnpj_fundo_classe
                ORDER BY
                    i.cnpj_fundo_classe,
                    i.dt_comptc DESC
                """
            )

            latest_reports = cur.fetchall()

            ranking = sorted(
                latest_reports,
                key=lambda row: row["vl_patrim_liq"] or 0,
                reverse=True,
            )[:limit]

            return {
                "metric": "net_asset_value",
                "total": len(ranking),
                "data": [
                    {
                        "position": index,
                        **fund,
                    }
                    for index, fund in enumerate(
                        ranking,
                        start=1,
                    )
                ],
            }
        

        
@app.get("/debug/database")
def debug_database():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    current_database() AS database,
                    current_schema() AS schema,
                    current_user AS user;
            """)

            connection_info = cur.fetchone()

            cur.execute("""
                SELECT
                    table_schema,
                    table_name
                FROM information_schema.tables
                WHERE table_name IN ('classe', 'informe_diario')
                ORDER BY table_schema, table_name;
            """)

            tables = cur.fetchall()

            return {
                "connection": connection_info,
                "tables": tables,
            }