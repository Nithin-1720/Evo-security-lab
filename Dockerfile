# ============================================================
# EVO VULNERABLE AI LAB
#
# INTENTIONALLY VULNERABLE CONTAINER.
# LAB USE ONLY.
# ============================================================

FROM python:3.11.6-slim-bullseye


#
# Deliberately hardcoded lab configuration.
#

ENV APP_ENV=lab
ENV DEBUG=true

ENV APP_SECRET=EVO-LAB-HARDCODED-CONTAINER-SECRET
ENV DB_PASSWORD=SuperUnsafeLabDatabasePassword_2026!

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


#
# INTENTIONALLY:
#
# - no package version pinning
# - old Debian base
# - unnecessary diagnostic utilities
#
RUN apt-get update && \
    apt-get install -y \
        curl \
        iputils-ping \
        procps \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


#
# Install actual application dependencies.
#

COPY requirements.txt /app/requirements.txt

RUN pip install \
    --no-cache-dir \
    -r /app/requirements.txt


#
# Also install deliberately vulnerable Python packages.
#
# They are isolated under /opt so they don't replace the
# application's working dependencies.
#

COPY legacy-python/requirements.txt /tmp/legacy-requirements.txt

RUN python -m pip install \
    --no-cache-dir \
    --target /opt/legacy-python \
    -r /tmp/legacy-requirements.txt


#
# Application source
#

COPY app /app/app
COPY scripts /app/scripts
COPY lab-data /app/lab-data
COPY lab_mcp /app/lab_mcp
COPY config /app/config


#
# INTENTIONALLY INSECURE FILE PERMISSIONS.
#

RUN chmod -R 0777 /app && \
    chmod -R 0777 /opt/legacy-python


#
# Two lab services may eventually exist:
#
# 8000 FastAPI
# 8001 MCP
#

EXPOSE 8000
EXPOSE 8001


#
# INTENTIONALLY NO USER DIRECTIVE.
#
# Container therefore runs as root.
#


CMD ["sh", "-c", "python -m scripts.init_lab && uvicorn app.main:app --host 0.0.0.0 --port 8000"]