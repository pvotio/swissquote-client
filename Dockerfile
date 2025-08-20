FROM python:3.13.7-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /opt/app
WORKDIR /opt/app

# System deps + MS ODBC 18 (Debian 12 / Bookworm) via signed keyring
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      gnupg \
      unixodbc \
      unixodbc-dev \
      libpq-dev \
 && mkdir -p /usr/share/keyrings \
 && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /usr/share/keyrings/msprod.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/msprod.gpg] https://packages.microsoft.com/repos/microsoft-debian-bookworm-prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools \
 # expose sqlcmd/bcp without editing shell profiles
 && ln -s /opt/mssql-tools/bin/sqlcmd /usr/local/bin/sqlcmd \
 && ln -s /opt/mssql-tools/bin/bcp /usr/local/bin/bcp \
 # cleanup
 && apt-get purge -y --auto-remove gnupg \
 && rm -rf /var/lib/apt/lists/*

# Python deps
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Non-root user
RUN useradd -m -r -d /opt/app -s /usr/sbin/nologin client \
 && chown -R client:client /opt/app
USER client

CMD ["python", "main.py"]
