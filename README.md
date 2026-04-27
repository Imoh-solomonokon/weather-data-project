# 🌤️ Automated Weather Data Pipeline

An end-to-end automated ELT pipeline that ingests live weather data from the Weatherstack API, loads it into a PostgreSQL database, transforms it using dbt, and visualises the results in an Apache Superset dashboard — all orchestrated by Apache Airflow running on Windows 11 WSL with Docker.

---

## 🎯 Problem Statement

Weather data is time-sensitive and continuously changing. Manually pulling and analysing this data is inefficient and not scalable. This project automates the full data journey — from API ingestion to business-ready dashboards — demonstrating a production-style ELT pipeline built with modern open-source data stack tools.

---

## 🛠️ Tools & Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow |
| Data Ingestion | Python (Requests, Psycopg2) |
| Data Warehouse | PostgreSQL (Dockerised) |
| Data Transformation | dbt (dbt-postgres 1.9) |
| Visualisation | Apache Superset (Dockerised) |
| Containerisation | Docker & Docker Compose |
| Data Source | Weatherstack API — New York |
| Environment | Windows 11 WSL (Ubuntu 24.04) |
| Language | Python, SQL |

---

## 🏗️ Architecture

```
Weatherstack API
      │
      ▼
┌─────────────────────────────────────────────────────┐
│                  Apache Airflow DAG                  │
│           (weather-api-dbt-orchestrator)             │
│                                                      │
│  Task 1 — PythonOperator                            │
│  ├── api_request.py  → fetch_data()                 │
│  └── insert_records.py → connect → create → insert  │
│                    │                                 │
│                    ▼                                 │
│  PostgreSQL (dev.raw_weather_data)                  │
│                    │                                 │
│  Task 2 — DockerOperator                            │
│  └── dbt-postgres:1.9 container → dbt run           │
│                    │                                 │
│         ┌──────────┴──────────┐                     │
│         ▼                     ▼                     │
│  stg_weather_data      daily_average                │
│  (deduplicated)        (avg temp & wind)            │
│         │                     │                     │
│         └──────────┬──────────┘                     │
│                    ▼                                 │
│           weather_report                             │
│    (clean weather records)                          │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
          Apache Superset Dashboard
          ├── Temperature Trends
          └── Average Wind Speed
```

---

## 📁 Project Structure

```
weather-data-project/
│
├── airflow/
│   └── dags/
│       └── orchestrator.py          # Airflow DAG — schedules and runs the pipeline
│
├── api-request/
│   ├── api_request.py               # Weatherstack API call + mock function for testing
│   └── insert_records.py            # PostgreSQL connection, table creation, data insert
│
├── dbt/
│   └── my_project/
│       ├── models/
│       │   ├── staging/
│       │   │   └── stg_weather_data.sql    # Cleans raw data, deduplicates by time
│       │   ├── mart/
│       │   │   ├── daily_average.sql       # Daily avg temperature & wind speed
│       │   │   └── weather_report.sql      # Clean weather records for reporting
│       │   └── sources/
│       │       └── sources.yml             # dbt source definition
│       └── dbt_project.yml
│
├── docker/
│   ├── docker-compose.yml           # Spins up PostgreSQL and Superset services
│   ├── docker-bootstrap.sh
│   ├── docker-init.sh
│   └── superset_config.py
│
├── postgres/
│   └── data/
│       ├── airflow_init.sql         # Initialises Airflow metadata database
│       └── superset_init.sql        # Initialises Superset database
│
├── notes.txt
└── README.md
```

---

## 🔄 Pipeline Workflow

### 1. 📡 Data Ingestion — Task 1 (PythonOperator)

The Airflow DAG runs on a **1-minute schedule** and triggers a `PythonOperator` that calls the `main()` function in `insert_records.py`. This function:

- Calls `fetch_data()` in `api_request.py` to hit the **Weatherstack API** for current New York weather
- Connects to the Dockerised PostgreSQL instance using `psycopg2`
- Creates the `dev.raw_weather_data` table if it does not already exist
- Inserts the following fields into the table:

| Field | Description |
|---|---|
| `city` | Location name |
| `temperature` | Current temperature (°C) |
| `weather_description` | Condition text (e.g. "Mist") |
| `wind_speed` | Wind speed in km/h |
| `time` | Local observation time |
| `inserted_at` | Pipeline run timestamp |
| `utc_offset` | UTC offset for the location |

> A `mock_fetch_data()` function is also included in `api_request.py` for local testing without consuming API credits.

---

### 2. 🔧 Data Transformation — Task 2 (DockerOperator + dbt)

Once ingestion completes, Airflow triggers a `DockerOperator` that spins up the official **dbt-postgres:1.9 Docker image** and runs `dbt run` against the warehouse. The dbt project follows a two-layer model architecture:

**Staging Layer** — `stg_weather_data.sql`
- Reads from `dev.raw_weather_data`
- Removes duplicate records using `ROW_NUMBER()` partitioned by `time` — ensures only the first record per observation window is kept
- Converts UTC timestamps to local time using the `utc_offset` field
- Renames columns to clean, readable names
- Materialised as a **table**

**Mart Layer** — `daily_average.sql`
- References `stg_weather_data`
- Aggregates daily averages of temperature and wind speed grouped by city and date
- Uses `ROUND(AVG()::numeric, 2)` for clean 2-decimal precision
- Materialised as a **table**

**Mart Layer** — `weather_report.sql`
- References `stg_weather_data`
- Selects clean, business-ready weather records for direct reporting use
- Serves as the primary table connected to the Superset dashboard
- Materialised as a **table**

---

### 3. 📊 Visualisation — Apache Superset

Superset is connected directly to the PostgreSQL warehouse as a database source. The dashboard surfaces:
- **Temperature Trends** — time series of temperature readings over pipeline runs
- **Average Wind Speed** — wind speed patterns aggregated by day

---

## ▶️ How to Run

### Prerequisites
- Windows 11 with WSL (Ubuntu 24.04)
- Docker Desktop with WSL integration enabled
- Python 3.8+
- Apache Airflow installed in WSL

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Imoh-solomonokon/weather-data-project.git
cd weather-data-project
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Add your Weatherstack API key in `api-request/api_request.py`:
```python
api_key = "your_api_key_here"
```

4. Start PostgreSQL and Superset via Docker Compose:
```bash
cd docker
docker-compose up -d
```

5. Start Airflow:
```bash
airflow standalone
```

6. Open the Airflow UI at `http://localhost:8080`, find the `weather-api-dbt-orchestrator` DAG and toggle it ON

7. Open Superset at `http://localhost:8088` to view the dashboard

---

## 💡 Lessons Learned

- Running dbt inside a **DockerOperator** is a clean production pattern that keeps the transformation environment isolated and reproducible
- Deduplication at the staging layer using `ROW_NUMBER()` is critical when ingesting time-series data on short schedules
- Separating ingestion, transformation, and visualisation into distinct layers makes the pipeline easy to debug and extend
- Docker Compose simplifies managing multiple services (PostgreSQL, Superset) with a single command
- A mock API function is invaluable during development — it prevents unnecessary API credit consumption while testing pipeline logic

---

## 👤 Author

**Imoh Solomonokon**
[LinkedIn](https://linkedin.com/in/imohsolomonokon) • [GitHub](https://github.com/YOUR_USERNAME)
