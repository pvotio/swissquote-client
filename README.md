# Swissquote Client Integration

This project implements a multi-threaded data integration pipeline for interacting with the **Swissquote API**, retrieving financial data for managed clients and injecting the data into a Microsoft SQL Server database. It is designed for financial analysts, advisors, and platform engineers looking to automate portfolio and transaction monitoring at scale.

## Overview

### Purpose

This application automates the following tasks:
- Authenticates with the Swissquote REST API using a bearer token.
- Retrieves data across several dimensions (clients, positions, transactions, static lists).
- Parallelizes API calls across data types using Python threading.
- Transforms the nested API responses into structured tabular formats.
- Inserts the transformed data into a SQL Server database.

The solution is intended to enable seamless integration of Swissquote data into a financial platform or analytics pipeline.

## Source of Data

Data is collected from the **Swissquote Asset Management API**, specifically:

- **Managed clients** and associated metadata.
- **Current holdings** (positions) by client.
- **Historical transactions** paginated per client.
- **Static lists** (securities metadata and taxonomy).

Base URL:  
```
https://bankingapi.swissquote.ch/am-interface-v2/api/v1/
```

A valid API token is required for access.

## Application Flow

The orchestration begins in `main.py`, executing the following sequence:

1. **Initialization**:
   - The `App` class initializes an internal `SwissQuote` client instance.
   - Configurations like retry/backoff are applied to ensure robust API interaction.

2. **Data Fetching**:
   - A list of client accounts is fetched first.
   - Threads are launched to pull positions, transactions, and static lists concurrently.
   - Transactions are paginated client-by-client for completeness.

3. **Transformation**:
   - The raw nested responses are passed to a `transformer.Agent` module.
   - Data is flattened and filtered to retain relevant fields only.

4. **Storage**:
   - Final cleaned data is inserted into respective SQL Server tables.
   - The `insert_data()` utility handles upsert/append logic.

## Project Structure

```
swissquote-client-main/
├── swissquote/               # API interaction logic and app orchestration
│   ├── client.py             # Raw endpoint wrappers
│   └── app.py                # Threaded data fetch logic
├── config/                   # Environment setup and logging
├── database/                 # MSSQL connectivity and helpers
├── transformer/              # Data cleaning and shaping
├── main.py                   # Pipeline entry point
├── .env.sample               # Example environment configuration
├── Dockerfile                # Containerization for deployment
```

## Environment Variables

Create a `.env` file based on `.env.sample`. Required variables include:

| Variable | Description |
|----------|-------------|
| `LOG_LEVEL` | Logging verbosity |
| `TOKEN` | Swissquote API bearer token |
| `STATICLISTS_OUTPUT_TABLE`, `TRANSACTIONS_OUTPUT_TABLE`, ... | Output MSSQL table names |
| `MSSQL_*` | SQL Server authentication parameters |
| `INSERTER_MAX_RETRIES`, `REQUEST_MAX_RETRIES`, `REQUEST_BACKOFF_FACTOR` | Retry behavior and exponential backoff settings |

## Docker Support

This project supports containerized deployment using Docker.

### Build
```bash
docker build -t swissquote-client .
```

### Run
```bash
docker run --env-file .env swissquote-client
```

## Requirements

Install Python dependencies using pip:
```bash
pip install -r requirements.txt
```

Key libraries include:
- `requests`: API communication
- `pandas`: Data transformation
- `SQLAlchemy`: Database interaction
- `fast-to-sql`: High-speed SQL insertion

## Running the App

Ensure `.env` is correctly set with all required variables, then:

```bash
python main.py
```

Logs will reflect API calls, data transformations, and database writes.

## License

This project is licensed under the MIT License. Access and use of Swissquote APIs must comply with their official data licensing and privacy terms.
