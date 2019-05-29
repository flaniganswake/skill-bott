#!/bin/bash
TS=$( date +%Y%m%d-%H%M )
mysqldump -u assess -pwessivem37 -h 127.0.0.1 assess > /var/opt/skillbott/assess/dumps/assess-$TS.sql
exit 0
