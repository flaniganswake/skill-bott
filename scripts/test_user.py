#!/usr/bin/env python3
import os
import random
import sys
import django


sys.path.insert(0, os.getcwd().replace('/skillbott/scripts', ''))
os.environ['DJANGO_SETTINGS_MODULE'] = 'skillbott.settings'
django.setup()
from orm.models import Answer, Inventory, Results, User
from utils import (perform_interests_analysis,
                   perform_skills_analysis,
                   perform_values_analysis)


"""
# delete users if necessary
users = User.objects.all()
print(str(len(users)))
for user in users:
    user.delete()
sys.exit(0)
"""

# debug and watch
watch = 0
debug = 0
if debug:
    if os.getcwd() == '/media/SDHC/projects/assess/scripts':
        debugfile = open('assess.dbg', 'w')
    else:
        debugfile = open('/tmp/assess.dbg', 'w')
    debugfile.write('... init_assess.py\n')

# parse the command line
options = 0
for arg in sys.argv:
    options = options + 1
if options != 2:
    print('usage: python3 test_user.py [# inventories completed (0-3)]')
    sys.exit(0)

# get # inventories completed
num_completed = int(sys.argv[1])
if num_completed > 3:
    print(str(num_completed), ' is not supported.')
    sys.exit(0)

if num_completed == 0:
    first_name = 'Yosemite'
    last_name = 'Sam'
elif num_completed == 1:
    first_name = 'Tweety'
    last_name = 'Bird'
elif num_completed == 2:
    first_name = 'Foghorn'
    last_name = 'Leghorn'
else:
    first_name = 'Demo'
    last_name = 'User'

# create user
try:
    user = User.objects.get(username__in=['user'+str(num_completed), 'demo'])
except User.DoesNotExist:
    if num_completed == 3:
        username = 'demo'
        user = User(username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=username + '@softseed.com',)
        user.set_password('demo37')
    else:
        user = User(username='user' + str(num_completed),
                    first_name=first_name,
                    last_name=last_name,
                    email='user' + str(num_completed)+'@softseed.com',)
        user.set_password('user' + str(num_completed))
    user.save()
    print('created: ', user.username, user.first_name, ' ', user.last_name)
else:
    if watch:
        print('... ', 'user'+str(num_completed), ' already exists')

if num_completed == 0:
    print('Completed 0 inventories')
    sys.exit(0)

# initialize results
try:
    results = Results.objects.get(user=user)
except Results.DoesNotExist:
    results = Results(user=user)
    results.save()

# take 'interests' inventory --------------------------------------------------
try:
    inventory = Inventory.objects.get(type='interests')
except Inventory.DoesNotExist:
    print('... inventory does not exist')
    sys.exit()
for category in inventory.categories.all():
    for topic in category.topics.all():
        # generate random answers
        yellow_int = random.randint(0, 2)
        if yellow_int:
            green_int = random.randint(1, 3)
        else:
            green_int = -1
        # test 'Other' with ''
        if topic.name == 'Other':
            yellow_int = -1
            green_int = -1
        answer = Answer(yellow=yellow_int,
                        green=green_int,
                        other='',  # test with ''
                        user=user,
                        topic=topic,
                        category=category,
                        inventory=inventory)
        answer.save()
        topic.answers.add(answer)

# perform 'interests' analysis
perform_interests_analysis(user, inventory, results)
if watch:
    print('interests_areas: ', str(results.interests_areas))

print(user.username + " completed inventory 'interests'")
if num_completed == 1:
    print('Completed 1 inventory')
    sys.exit(0)

# take 'skills' inventory -----------------------------------------------------
try:
    inventory = Inventory.objects.get(type='skills')
except Inventory.DoesNotExist:
    print('... inventory does not exist')
    sys.exit()
top_categories = results.get_top_cats_list(inventory)
if watch:
    print('top_categories: ', top_categories)

for category in top_categories:
    for topic in category.topics.all():
        # generate random answers
        yellow_int = random.randint(0, 2)
        green_int = random.randint(1, 3)
        answer = Answer(yellow=yellow_int,
                        green=green_int,
                        other='Test',
                        user=user,
                        topic=topic,
                        category=category,
                        inventory=inventory)
        answer.save()
        topic.answers.add(answer)

# perform 'skills' analysis
perform_skills_analysis(user, inventory, top_categories, results)
if watch:
    print('skills_current: ', str(results.skills_current))
    print('skills_training: ', str(results.skills_training))

print(user.username + " completed inventory 'skills'")
if num_completed == 2:
    print('Completed 2 inventories')
    sys.exit(0)

# take 'values' inventory -----------------------------------------------------
try:
    inventory = Inventory.objects.get(type='values')
except Inventory.DoesNotExist:
    print('... inventory does not exist')
    sys.exit()
top_categories = results.get_top_cats_list(inventory)

for category in top_categories:
    for topic in category.topics.all():
        # generate random answers
        yellow_int = random.randint(0, 2)
        green_int = random.randint(1, 3)
        answer = Answer(yellow=yellow_int,
                        green=green_int,
                        other='Test',
                        user=user,
                        topic=topic,
                        category=category,
                        inventory=inventory)
        answer.save()
        topic.answers.add(answer)

# perform 'values' analysis
perform_values_analysis(user, inventory, top_categories, results)
if watch:
    print('your_values: ', str(results.your_values))
    print('job_values: ', str(results.job_values))

print(user.username + " completed inventory 'values'")
print('Completed 3 inventories')
sys.exit(0)
