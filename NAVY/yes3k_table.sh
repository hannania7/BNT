#!/bin/bash

# PGPASSWORD=Iois /usr/pgsql-12/bin/psql -h 34.1.1.69 -U iois -d iois -f /DATA/PYTHON/source/create_table/yes3k_table.sql >> /DATA/PYTHON/source/create_table/log/yes3k_table.txt
PGPASSWORD=Iois /usr/pgsql-9.6/bin/psql -h greenblue.iptime.org -U iois -p 8751 -d iois -f /DATA/NAVY/source/yes3k_table.sql >> /DATA/NAVY/source/LOG/yes3k_table.txt
echo after [`date`] >> /DATA/NAVY/source/LOG/del_result.txt