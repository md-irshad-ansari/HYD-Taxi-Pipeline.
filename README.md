# HYD Taxi Trip Data Engineering Pipeline

End-to-end data engineering project processing NYC Yellow Taxi trip records.

## Architecture

`
Source (TLC) -> Ingestion (Python) -> DuckDB (Bronze/Silver/Gold) -> dbt -> Airflow -> Power BI
`

## Tech Stack

| Layer | Tool |
|:---|:---|
| Ingestion | Python (requests + polars) |
| Warehouse | DuckDB |
| Transformation | dbt-core (dbt-duckdb) |
| Orchestration | Apache Airflow |
| Dashboard | Power BI Desktop |

## Project Structure

`
nyc-taxi-pipeline/
├── ingestion/          # Data ingestion scripts
├── data/               # Data storage (gitignored)
├── transform/          # dbt project
├── airflow/            # Airflow DAGs
├── powerbi/            # Power BI files
├── scripts/            # Utility scripts
└── tests/              # Tests
`

## Setup

Coming soon...
