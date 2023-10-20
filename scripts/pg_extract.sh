#!/bin/bash
[ $# -lt 2 ] && { echo "Usage: $0 <postgresql dump> <dbname>"; exit 1; }
sed  "/connect.*$2/,\$!d" $1 | sed "/PostgreSQL database dump complete/,\$d"
