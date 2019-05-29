#!/bin/bash
DOCKER_ID=$1
if [ -z "$DOCKER_ID" ]; then
    echo "Error: missing docker ID"
    exit 1
fi
echo "... running migrations"
docker exec -ti $DOCKER_ID sh -c "python3 manage.py migrate"
echo "... loading fixtures"
docker exec -ti $DOCKER_ID sh -c "python3 manage.py loaddata fixtures/assess.json"
echo "... creating test users"
docker exec -ti $DOCKER_ID sh -c "./scripts/test_users.sh"
echo "... collecting static files"
docker exec -ti $DOCKER_ID sh -c "python3 manage.py collectstatic --noinput > /dev/null"
echo "... creating superuser"
docker exec -ti $DOCKER_ID sh -c "python3 manage.py createsuperuser"
