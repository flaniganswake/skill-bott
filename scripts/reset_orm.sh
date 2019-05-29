#!/bin/sh

# SET foreign_key_checks = 0; drop tables
echo ...resetting the database

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_answer;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_answer;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_category;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_category;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_category_topics;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_category_topics;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_choice;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_choice;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_categories;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_categories;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_green_choices;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_green_choices;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_yellow_choices;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_inventory_yellow_choices;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_results;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_results;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_results_top_categories;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_results_top_categories;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic_answers;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic_answers;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_customer;'

echo "mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_topic_answers;'"
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 0; drop table orm_customer_users;'

echo SET foreign_key_checks = 1;
mysql --user=assess --password=wessivem37 assess --execute='SET foreign_key_checks = 1;'

# initialize django orm
echo ...all orm tables dropped

# reset old migrations
#echo ... resetting old migrations
#../.././manage.py migrate --all --fake --delete-ghost-migrations

echo Done.
