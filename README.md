# SwissQuote Client
## Overview
SwissQuote Client is a Python-based tool for interacting with the SwissQuote Banking API. It retrieves financial data such as managed clients, positions, transactions, and buying power, processes the data, and stores it in an MSSQL database for further analysis.

## Features
- Fetches client data, stock positions, transactions, and exchange rates from SwissQuote.
- Implements retry mechanisms and backoff strategies for robust API communication.
- Transforms raw financial data into structured formats for analysis.
- Stores processed data in a Microsoft SQL Server database.
- Supports multi-threaded data retrieval for improved performance.

## Installation
### Prerequisites
- Python 3.10+
- Microsoft SQL Server
- Docker (optional, for containerized execution)

### Setup
Clone the repository:

```bash
git clone https://github.com/arqs-io/swissquote-client.git
cd swissquote-client.git
```

Install dependencies:

`pip install -r requirements.txt`

Set up environment variables:

- Copy .env.sample to .env
- Edit .env to include your database and API credentials.

Run the application:
`python main.py`

## Docker Usage

To run the application using Docker:


```bash
docker build -t swissquote-client.git .
docker run --env-file .env swissquote-client.git
```

## Contributing
- Fork the repository.
- Create a feature branch: git checkout -b feature-branch
- Commit changes: git commit -m "Add new feature"
- Push to the branch: git push origin feature-branch
- Open a Pull Request.