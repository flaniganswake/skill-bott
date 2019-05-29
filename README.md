
# Docker SkillBott

Python 3.7 - Django 2.1 - MySQL 8.0

### MySQL initialization

```
python3 manage.py migrate

python3 manage.py loaddata fixtures/initial_data.json"
```

Loading from scratch

```
./scripts/initassess.sh - loads 'interests', 'skills' and 'values' tables

./scripts/testusers.sh - creates 4 testusers - with 0, 1, 2, 3 inventories taken
```

Test users login

```
user:password = user<num>:user<num><num><num>
```

### Docker instructions


Get the containers running then ps for skillbott_app CONTAINER ID

```
docker-compose up -d
docker ps
```

This script initializes the database with assessments, test users
and creates a superuser for the /admin view

```
./docker_init.sh <CONTAINER ID>
```
