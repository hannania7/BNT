#!/bin/bash

# 운영서버
# PGPASSWORD=Iois /usr/pgsql-12/bin/psql -h 34.1.1.69 -U iois -d iois -f /DATA/PYTHON/source/create_table/ww3_table.sql >> /DATA/PYTHON/source/create_table/log/ww3_table.txt

# 개발서버
PGPASSWORD=Iois /usr/pgsql-9.6/bin/psql -h greenblue.iptime.org -U iois -p 8751 -d iois -f /DATA/NAVY/source/ww3_table.sql >> /DATA/NAVY/source/LOG/ww3_table.txt


echo after [`date`] >> /DATA/NAVY/source/LOG/del_result.txt