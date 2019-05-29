#!/bin/sh

# initialize orm with migrations
echo ...initializing the database
#../../manage.py syncdb
#../../manage.py schemamigration orm --initial
../../manage.py migrate orm
