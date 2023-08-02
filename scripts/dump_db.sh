#!/bin/sh
# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

# Dump db content to sql file and copy it to s3: should be run from package root directory

# Set environment variables from .env
export $(grep -v '^#' .env | xargs)

mkdir -p db_backup
fname=db_backup/dump_$(date +%Y-%m-%d_%H_%M_%S).sql
echo "Dumping db content to ${fname}"
docker compose exec -T db pg_dumpall -c -U "${POSTGRES_USER}" > "${fname}"

if [ ! -s "$fname" ]; then
  echo "Dump failed"
  exit 1
fi

if [ -z "$BUCKET_DB_BACKUP_FOLDER" ]; then
  echo "BUCKET_DB_BACKUP_FOLDER not defined"
  exit 1
fi

dest=$BUCKET_DB_BACKUP_FOLDER/$(basename "${fname}")
echo "Copying ${fname} to s3: ${BUCKET_NAME}/${dest}"
docker compose exec -T backend python -c "import asyncio; from app.services import bucket_service; print(asyncio.run(bucket_service.upload_file(\"${dest}\", \"${fname}\")))"
