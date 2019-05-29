''' utility functions '''
import sys
import os
import operator
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from orm.models import Answer

sys.path.insert(0, os.getcwd().replace('/scripts', ''))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


def send_email(text):

    msg = MIMEMultipart()
    msg['Subject'] = 'Test'
    msg['From'] = 'assess@assess.skillbott.com'
    msg['To'] = 'flaniganswake@protonmail.com'
    content = MIMEText(text, 'plain')
    msg.attach(content)
    s = smtplib.SMTP('localhost')
    s.sendmail('assess@assess.skillbott.com', ['flaniganswake@gmail.com'],
               msg.as_string())
    s.quit()


def perform_interests_analysis(user, inventory, results):

    # initialize
    yellow_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    y_totals0 = 0
    y_totals1 = 0
    y_totals2 = 0
    green_answers = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    g_totals1 = 0
    g_totals2 = 0
    g_totals3 = 0

    # total yellow and green answers
    answers = Answer.objects.filter(user=user, inventory=inventory)
    for answer in answers:
        yellow_answers[str(answer.topic.id)] = int(answer.yellow)
        green_answers[str(answer.topic.id)] = int(answer.green)
 
        # totals for analysis
        if answer.yellow == 0:
            if answer.topic.category.type in yellow_totals0:
                y_totals0 = y_totals0 + 1
            else:
                y_totals0 = 1
            yellow_totals0[answer.topic.category.type] = y_totals0
        elif answer.yellow == 1:
            if answer.topic.category.type in yellow_totals1:
                y_totals1 = y_totals1 + 1
            else:
                y_totals1 = 1
            yellow_totals1[answer.topic.category.type] = y_totals1
        elif answer.yellow == 2:
            if answer.topic.category.type in yellow_totals2:
                y_totals2 = y_totals2 + 1
            else:
                y_totals2 = 1
            yellow_totals2[answer.topic.category.type] = y_totals2
        if answer.green == 1:
            if answer.topic.category.type in green_totals1:
                g_totals1 = g_totals1 + 1
            else:
                g_totals1 = 1
            green_totals1[answer.topic.category.type] = g_totals1
        elif answer.green == 2:
            if answer.topic.category.type in green_totals2:
                g_totals2 = g_totals2 + 1
            else:
                g_totals2 = 1
            green_totals2[answer.topic.category.type] = g_totals2
        elif answer.green == 3:
            if answer.topic.category.type in green_totals3:
                g_totals3 = g_totals3 + 1
            else:
                g_totals3 = 1
            green_totals3[answer.topic.category.type] = g_totals3

    # initialize empty keys
    for category in inventory.categories.all():
        if category.type not in yellow_totals0:
            yellow_totals0[category.type] = 0
        if category.type not in yellow_totals1:
            yellow_totals1[category.type] = 0
        if category.type not in yellow_totals2:
            yellow_totals2[category.type] = 0
        if category.type not in green_totals1:
            green_totals1[category.type] = 0
        if category.type not in green_totals2:
            green_totals2[category.type] = 0
        if category.type not in green_totals3:
            green_totals3[category.type] = 0

    # set results.top_categories list
    yellow_totals = {}
    for category in inventory.categories.all():
        yellow_totals0[category.type] = 0
        yellow_totals1[category.type] = yellow_totals1[category.type]
        yellow_totals2[category.type] = yellow_totals2[category.type]*2
        yellow_totals[category.type] = yellow_totals0[category.type] + \
            yellow_totals1[category.type] + yellow_totals2[category.type]
    top_categories = results.set_top_cats(yellow_totals, inventory)

    # set results.interests_areas
    green_modes = {}
    for category in top_categories:
        green_max = max([green_totals1[category.type],
                         green_totals2[category.type],
                         green_totals3[category.type]])
        if green_totals1[category.type] == green_max:
            green_modes[category.type] = 1
        elif green_totals2[category.type] == green_max:
            green_modes[category.type] = 2
        else:
            green_modes[category.type] = 3
    interests_areas = results.set_interests_areas(
        inventory, top_categories, green_modes)

    # save 'interests' results
    results.interests_complete = True
    results.save()
    return 1


def perform_skills_analysis(user, inventory, top_categories, results):

    # initialize
    yellow_answers = {}
    green_answers = {}
    other_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    y_totals0 = 0
    y_totals1 = 0
    y_totals2 = 0
    g_totals1 = 0
    g_totals2 = 0
    g_totals3 = 0  

    # load user answers in context
    answers = Answer.objects.filter(user=user, inventory=inventory)
    for answer in answers:
        yellow_answers[str(answer.topic.id)] = int(answer.yellow)
        green_answers[str(answer.topic.id)] = int(answer.green)
        other_answers[str(answer.topic.id)] = answer.other

        # totals for analysis
        if answer.yellow == 0:
            if answer.topic.category.type in yellow_totals0:
                y_totals0 = y_totals0 + 1
            else:
                y_totals0 = 1
            yellow_totals0[answer.topic.category.type] = y_totals0
        elif answer.yellow == 1:
            if answer.topic.category.type in yellow_totals1:
                y_totals1 = y_totals1 + 1
            else:
                y_totals1 = 1
            yellow_totals1[answer.topic.category.type] = y_totals1
        elif answer.yellow == 2:
            if answer.topic.category.type in yellow_totals2:
                y_totals2 = y_totals2 + 1
            else:
                y_totals2 = 1
            yellow_totals2[answer.topic.category.type] = y_totals2
        if answer.green == 1:
            if answer.topic.category.type in green_totals1:
                g_totals1 = g_totals1 + 1
            else:
                g_totals1 = 1
            green_totals1[answer.topic.category.type] = g_totals1
        elif answer.green == 2:
            if answer.topic.category.type in green_totals2:
                g_totals2 = g_totals2 + 1
            else:
                g_totals2 = 1
            green_totals2[answer.topic.category.type] = g_totals2
        elif answer.green == 3:
            if answer.topic.category.type in green_totals3:
                g_totals3 = g_totals3 + 1
            else:
                g_totals3 = 1
            green_totals3[answer.topic.category.type] = g_totals3

    for category in top_categories:
        if category.type not in yellow_totals0:
            yellow_totals0[category.type] = 0
        if category.type not in yellow_totals1:
            yellow_totals1[category.type] = 0
        if category.type not in yellow_totals2:
            yellow_totals2[category.type] = 0
        if category.type not in green_totals1:
            green_totals1[category.type] = 0
        if category.type not in green_totals2:
            green_totals2[category.type] = 0
        if category.type not in green_totals3:
            green_totals3[category.type] = 0

    # calculate weighted yellow totals
    yellow_totals = {}
    for category in top_categories:
        yellow_totals0[category.type] = 0
        yellow_totals1[category.type] = yellow_totals1[category.type]
        yellow_totals2[category.type] = yellow_totals2[category.type]*2
        yellow_totals[category.type] = yellow_totals0[category.type] + \
            yellow_totals1[category.type] + yellow_totals2[category.type]

    # calculate weighted green totals
    green_totals = {}
    for category in top_categories:
        green_totals1[category.type] = 0
        green_totals2[category.type] = green_totals2[category.type]
        green_totals3[category.type] = green_totals3[category.type]*2
        green_totals[category.type] = green_totals1[category.type] + \
            green_totals2[category.type] + green_totals3[category.type]

    # set results.skills_current
    skills_current = results.set_skills_current(top_categories, yellow_totals)

    # set results.skills_training
    skills_training = results.set_skills_training(top_categories, green_totals)

    # save 'skills' results
    results.skills_complete = True
    results.save()
    return 1


def perform_values_analysis(user, inventory, categories, results):

    # initialize
    yellow_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    y_totals0 = 0
    y_totals1 = 0
    y_totals2 = 0
    green_answers = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    g_totals1 = 0
    g_totals2 = 0
    g_totals3 = 0

    # total yellow and green answers
    answers = Answer.objects.filter(user=user, inventory=inventory)
    for answer in answers:
        yellow_answers[str(answer.topic.id)] = int(answer.yellow)
        green_answers[str(answer.topic.id)] = int(answer.green)
 
        # totals for analysis
        if answer.yellow == 0:
            if answer.topic.category.type in yellow_totals0:
                y_totals0 = y_totals0 + 1
            else:
                y_totals0 = 1
            yellow_totals0[answer.topic.category.type] = y_totals0
        elif answer.yellow == 1:
            if answer.topic.category.type in yellow_totals1:
                y_totals1 = y_totals1 + 1
            else:
                y_totals1 = 1
            yellow_totals1[answer.topic.category.type] = y_totals1
        elif answer.yellow == 2:
            if answer.topic.category.type in yellow_totals2:
                y_totals2 = y_totals2 + 1
            else:
                y_totals2 = 1
            yellow_totals2[answer.topic.category.type] = y_totals2
        if answer.green == 1:
            if answer.topic.category.type in green_totals1:
                g_totals1 = g_totals1 + 1
            else:
                g_totals1 = 1
            green_totals1[answer.topic.category.type] = g_totals1
        elif answer.green == 2:
            if answer.topic.category.type in green_totals2:
                g_totals2 = g_totals2 + 1
            else:
                g_totals2 = 1
            green_totals2[answer.topic.category.type] = g_totals2
        elif answer.green == 3:
            if answer.topic.category.type in green_totals3:
                g_totals3 = g_totals3 + 1
            else:
                g_totals3 = 1
            green_totals3[answer.topic.category.type] = g_totals3

    # initialize empty keys
    for category in categories:
        if category.type not in yellow_totals0:
            yellow_totals0[category.type] = 0
        if category.type not in yellow_totals1:
            yellow_totals1[category.type] = 0
        if category.type not in yellow_totals2:
            yellow_totals2[category.type] = 0
        if category.type not in green_totals1:
            green_totals1[category.type] = 0
        if category.type not in green_totals2:
            green_totals2[category.type] = 0
        if category.type not in green_totals3:
            green_totals3[category.type] = 0

    # calculate weighted yellow totals
    yellow_totals = {}
    for category in categories:
        yellow_totals0[category.type] = 0
        yellow_totals1[category.type] = yellow_totals1[category.type]
        yellow_totals2[category.type] = yellow_totals2[category.type]*2
        yellow_totals[category.type] = yellow_totals0[category.type] + \
            yellow_totals1[category.type] + yellow_totals2[category.type]

    # calculate weighted green totals
    green_totals = {}
    for category in categories:
        green_totals1[category.type] = 0
        green_totals2[category.type] = green_totals2[category.type]
        green_totals3[category.type] = green_totals3[category.type]*2
        green_totals[category.type] = green_totals1[category.type] + \
            green_totals2[category.type] + green_totals3[category.type]

    # set results.your_values
    your_values = results.set_your_values(categories, yellow_totals)

    # set results.job_values
    job_values = results.set_job_values(categories, green_totals)

    # make dicts of the topic answers - then sort and get top 3
    your_values_dict = {}
    job_values_dict = {}
    your_values_top3 = {}
    job_values_top3 = {}
    for category in categories:
        your_values_dict[category.type] = {}
        job_values_dict[category.type] = {}
        answers = Answer.objects.filter(user=user, inventory=inventory,
                                        category=category)
        for answer in answers:
            your_values_dict[category.type][str(answer.topic.name)] = \
                int(answer.yellow)
            job_values_dict[category.type][str(answer.topic.name2)] = \
                int(answer.green)

        # now sort them
        your_values_dict[category.type] = \
            sorted(your_values_dict[category.type].items(),
                   key=operator.itemgetter(1), reverse=True)
        job_values_dict[category.type] = \
            sorted(job_values_dict[category.type].items(),
                   key=operator.itemgetter(1), reverse=True)
        
        # now get the top 3 topics for this category
        your_values_top3[category.type] = {}
        ndx = 0
        for key, _ in your_values_dict[category.type]:
            your_values_top3[category.type][ndx] = key
            ndx = ndx+1
            if ndx == 3:
                break
        job_values_top3[category.type] = {}
        ndx = 0
        for key, _ in job_values_dict[category.type]:
            job_values_top3[category.type][ndx] = key
            ndx = ndx+1
            if ndx == 3:
                break

    # save the results
    your_values_top15_dict = results.set_your_values_top15(
        categories, your_values_top3)
    job_values_top15_dict = results.set_job_values_top15(
        categories, job_values_top3)

    # save 'values' results
    results.values_complete = True
    results.set_completion_date()
    results.save()
    return 1