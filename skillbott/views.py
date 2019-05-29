from django.http import HttpResponse
from django.http import QueryDict
from django.template import Template, Context, RequestContext
from django.shortcuts import render_to_response, render
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from orm.models import Answer, Inventory, Results
from orm.templatetags import filters
from utils import perform_interests_analysis, perform_skills_analysis
import settings
import operator
import os

import logging
logger = logging.getLogger()


def home(request):

    if request.user.is_authenticated:
        try:
            results = Results.objects.get(user=request.user)
        except ObjectDoesNotExist:
            results = Results(user=request.user)
            results.save()
    else:
        results = False

    """ retrieve user tokens
    users = User.objects.all()
    for user in users:
        token, created = Token.objects.get_or_create(user=user)
        logger.debug("token test: "+user.username+" - "+token.key)
    """

    inventories = Inventory.objects.all()
    context = {'inventories': inventories,
               'results': results,
               'home': 1}
    return render(request, 'home.html', context)


def start_demo(request):

    if request.user.is_authenticated:
        logout(request)

    # login to demo_user programmatically
    user = authenticate(username='demo', password='demo37')
    if user is not None:
        if user.is_active:
            login(request, user)

    return home(request)


@login_required
def interests_inventory(request, start=None):

    try:
        inventory = Inventory.objects.get(type='interests')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response('inventory.html', context={'error': error})

    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=request.user)
        results.save()

    # initialize context
    yellow_widths = {}
    green_widths = {}
    yellow_answers = {}
    green_answers = {}
    other_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    started = 0
 
    # load yellow_widths
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '40px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '60px'
        else:
            yellow_widths[str(ndx)] = '50px'
        ndx=ndx+1

    # load green_widths
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '60px'
        elif ndx == 1:
            green_widths[str(ndx)] = '105px'
        else:
            green_widths[str(ndx)] = '90px'
        ndx=ndx+1

    if request.method == 'POST':

        # retrieve user answers and save
        started = 1
        complete = True
        for category in inventory.categories.all():
            y_totals0 = 0
            y_totals1 = 0
            y_totals2 = 0
            g_totals1 = 0
            g_totals2 = 0
            g_totals3 = 0

            for topic in category.topics.all():
                yellow_id = 'yellow_' + str(topic.id)
                yellow_int = int(request.POST.get(yellow_id, -1))
                green_id = 'green_' + str(topic.id)
                green_int = int(request.POST.get(green_id, -1))
                other_id = 'other_' + str(topic.id)
                other_text = request.POST.get(other_id, '')

                # handle 'Other'
                if topic.name == 'Other':
                    if other_text == '':
                        yellow_int = -1
                        green_int = -1

                # check if answer already exists
                try:
                    answer = Answer.objects.get(user=request.user, topic=topic, inventory=inventory)
                    answer.yellow = yellow_int
                    answer.green = green_int
                    answer.other = other_text
                    answer.save()
                except ObjectDoesNotExist:
                    answer = Answer(yellow=yellow_int, 
                                    green=green_int, 
                                    other=other_text, 
                                    user=request.user, 
                                    topic=topic, 
                                    category=category, 
                                    inventory=inventory)
                    answer.save()
                    topic.answers.add(answer)       

                # load user answers in context
                yellow_answers[str(topic.id)] = int(yellow_int)
                green_answers[str(topic.id)] = int(green_int)
                other_answers[str(topic.id)] = other_text
                if yellow_int == -1 and topic.name != 'Other':
                    complete = False
                if yellow_int > 0 and green_int == -1:
                    # answer is incomplete - if no green
                    yellow_answers[str(topic.id)] = -1
                    complete = False

                # compute totals for analysis
                if yellow_int == 0:
                    y_totals0 = y_totals0 + 1
                    yellow_totals0[category.type] = y_totals0
                elif yellow_int == 1:
                    y_totals1 = y_totals1 + 1
                    yellow_totals1[category.type] = y_totals1
                elif yellow_int == 2:
                    y_totals2 = y_totals2 + 1
                    yellow_totals2[category.type] = y_totals2
                if green_int == 1:
                    g_totals1 = g_totals1 + 1
                    green_totals1[category.type] = g_totals1
                elif green_int == 2:
                    g_totals2 = g_totals2 + 1
                    green_totals2[category.type] = g_totals2
                elif green_int == 3:
                    g_totals3 = g_totals3 + 1
                    green_totals3[category.type] = g_totals3

        if complete:
            # perform 'interests' analysis
            perform_interests_analysis(request.user, inventory, results)
        else:
            results.interests_complete = False
            results.save()
             
    else:  # request.method == 'GET':

        # load user answers in context
        answers = Answer.objects.filter(user=request.user, inventory=inventory)

        # if no answers exist yet - go to instructions page
        if answers.count() == 0:
            if start == None:
                return render_to_response('interests_instructions.html',
                                          context={'inventory': inventory})

        for answer in answers:
            started = 1
            yellow_answers[str(answer.topic.id)] = int(answer.yellow)
            green_answers[str(answer.topic.id)] = int(answer.green)
            other_answers[str(answer.topic.id)] = answer.other
            if int(answer.yellow) > 0 and int(answer.green) == -1:
                # answer is incomplete - if no green
                yellow_answers[str(answer.topic.id)] = -1

            # compute totals for analysis
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

    # set categories
    categories = inventory.categories.all

    context = {
        'inventory': inventory,
        'categories': categories,
        'yellow_answers': yellow_answers, 
        'green_answers': green_answers, 
        'other_answers': other_answers,
        'yellow_widths': yellow_widths,
        'green_widths': green_widths,
        'yellow_totals0': yellow_totals0,
        'yellow_totals1': yellow_totals1,
        'yellow_totals2': yellow_totals2,
        'green_totals1': green_totals1,
        'green_totals2': green_totals2,
        'green_totals3': green_totals3,
        'complete': results.interests_complete,
        'started': started,
        'results': results,
        'inventory_page': 1,
    }
    logger.debug("Inventory context: %r" % context)
    return render_to_response('inventory.html', context)


@login_required
def interests_analysis(request):

    try:
        inventory = Inventory.objects.get(type='interests')
    except ObjectDoesNotExist:
        context = {'error': 'Inventory does not exist.'}
        return render_to_response('interests_analysis.html', context)

    # get user results
    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=user)
        results.save()

    if request.method == 'POST': # the user wants to reorder the top categories
        new_order = request.POST.get("new_order").split(',')
        results.set_new_order_top_cats(new_order)

    # load table cell widths
    yellow_widths = {}
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '40px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '60px'
        else:
            yellow_widths[str(ndx)] = '50px'
        ndx=ndx+1
    green_widths = {}
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '60px'
        elif ndx == 1:
            green_widths[str(ndx)] = '105px'
        else:
            green_widths[str(ndx)] = '90px'
        ndx=ndx+1

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
    answers = Answer.objects.filter(user=request.user, inventory=inventory)
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

    # calculate weighted yellow totals
    yellow_totals = {}
    for category in inventory.categories.all():
        yellow_totals0[category.type] = 0
        yellow_totals1[category.type] = yellow_totals1[category.type]
        yellow_totals2[category.type] = yellow_totals2[category.type]*2
        yellow_totals[category.type] = yellow_totals0[category.type] + yellow_totals1[category.type] + yellow_totals2[category.type]

    # get top_categories
    categories = results.get_top_cats_list(inventory)

    # calculate green modes
    green_modes = {}
    for category in categories:
         green_max = max([green_totals1[category.type], green_totals2[category.type], green_totals3[category.type]])
         if green_totals1[category.type] == green_max:
             green_modes[category.type] = 1
         elif green_totals2[category.type] == green_max:
             green_modes[category.type] = 2
         else:
             green_modes[category.type] = 3
    
    # get interests_areas
    interests_areas = results.get_interests_areas_dict(categories)

    context = { 'inventory': inventory,
                'categories': categories,
                'yellow_answers': yellow_answers, 
                'green_answers': green_answers, 
                'other_answers': other_answers,
                'yellow_widths': yellow_widths,
                'green_widths': green_widths,
                'yellow_totals0': yellow_totals0,
                'yellow_totals1': yellow_totals1,
                'yellow_totals2': yellow_totals2,
                'yellow_totals': yellow_totals,
                'green_totals1': green_totals1,
                'green_totals2': green_totals2,
                'green_totals3': green_totals3,
                'green_modes': green_modes,
                'interests_areas': interests_areas,
                'results': results, 
                'analysis_page': 1,
    }
    return render_to_response('interests_analysis.html',
                              context=context)


@login_required
def interests_summary(request):

    try:
        inventory = Inventory.objects.get(type='interests')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'interests_summary.html',
            context={'error': 'Inventory does not exist.'})

    context = { 'inventory': inventory, 
                'summary_page': 1,
    }
    return render_to_response('interests_summary.html',
                              context=context)


@login_required
def interests_instructions(request):

    try:
        inventory = Inventory.objects.get(type='interests')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'interests_instructions.html',
            context={'error': 'Inventory does not exist.'})

    context = { 'inventory': inventory, 
                'instructions_page': 1,
    }
    return render_to_response('interests_instructions.html',
                              context=context)


@login_required
def skills_inventory(request):

    try:
        inventory = Inventory.objects.get(type='skills')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response('inventory.html',
                                  context={'error': error})

    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=request.user)
        results.save()

    # initialize context
    yellow_widths = {}
    green_widths = {}
    yellow_answers = {}
    green_answers = {}
    other_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    started = 0

    # load yellow_widths
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '50px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '90px'
        else:
            yellow_widths[str(ndx)] = '50px'
        ndx=ndx+1

    # load green_widths
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '80px'
        elif ndx == 1:
            green_widths[str(ndx)] = '100px'
        else:
            green_widths[str(ndx)] = '90px'
        ndx=ndx+1

    # initialize categories
    categories = results.get_top_cats_list(inventory)

    if request.method == 'POST':

        # retrieve user answers and save
        started = 1
        complete = True
        for category in categories:
            y_totals0 = 0
            y_totals1 = 0
            y_totals2 = 0
            g_totals1 = 0
            g_totals2 = 0
            g_totals3 = 0

            for topic in category.topics.all():
                yellow_id = 'yellow_' + str(topic.id)
                yellow_int = int(request.POST.get(yellow_id, -1))
                green_id = 'green_' + str(topic.id)
                green_int = int(request.POST.get(green_id, -1))
                other_id = 'other_' + str(topic.id)
                other_text = request.POST.get(other_id, '')

                # both yellow and green must exist
                if yellow_int == -1:
                    green_int = -1
                if green_int == -1:
                    yellow_int = -1

                # handle 'Other'
                if topic.name == 'Other':
                    if other_text == '':
                        yellow_int = -1
                        green_int = -1
              
                # check if answer already exists
                try:
                    answer = Answer.objects.get(user=request.user, topic=topic, inventory=inventory)
                    answer.yellow = yellow_int
                    answer.green = green_int
                    answer.other = other_text
                    answer.save()
                except ObjectDoesNotExist:
                    answer = Answer(yellow=yellow_int, 
                                    green=green_int, 
                                    other=other_text, 
                                    user=request.user, 
                                    topic=topic, 
                                    category=category,
                                    inventory=inventory)
                    answer.save()
                    topic.answers.add(answer)       

                # load user answers in context
                yellow_answers[str(topic.id)] = yellow_int
                green_answers[str(topic.id)] = green_int
                other_answers[str(topic.id)] = other_text
                if yellow_int == -1 and topic.name != 'Other':
                    complete = False
                if yellow_int > 0 and green_int == -1:
                    # answer is incomplete - if no green
                    yellow_answers[str(topic.id)] = -1
                    complete = False

                # compute totals for analysis
                if yellow_int == 0:
                    y_totals0 = y_totals0 + 1
                    yellow_totals0[category.type] = y_totals0
                elif yellow_int == 1:
                    y_totals1 = y_totals1 + 1
                    yellow_totals1[category.type] = y_totals1
                elif yellow_int == 2:
                    y_totals2 = y_totals2 + 1
                    yellow_totals2[category.type] = y_totals2
                if green_int == 1:
                    g_totals1 = g_totals1 + 1
                    green_totals1[category.type] = g_totals1
                elif green_int == 2:
                    g_totals2 = g_totals2 + 1
                    green_totals2[category.type] = g_totals2
                elif green_int == 3:
                    g_totals3 = g_totals3 + 1
                    green_totals3[category.type] = g_totals3

        if complete:
            # perform 'skills' analysis
            perform_skills_analysis(request.user, inventory, categories, results)
        else:
            results.skills_complete = False
            results.save()
        
    else: # request.method == 'GET':

        # load user answers in context
        answers = Answer.objects.filter(user=request.user, inventory=inventory)
        for answer in answers:
            started = 1
            yellow_answers[str(answer.topic.id)] = int(answer.yellow)
            green_answers[str(answer.topic.id)] = int(answer.green)
            other_answers[str(answer.topic.id)] = answer.other
            if int(answer.yellow) > 0 and int(answer.green) == -1:
                # answer is incomplete - if no green
                yellow_answers[str(answer.topic.id)] = -1

            # compute totals for analysis
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

    context = { 'inventory': inventory,
                'categories': categories,
                'yellow_answers': yellow_answers, 
                'green_answers': green_answers, 
                'other_answers': other_answers,
                'yellow_widths': yellow_widths,
                'green_widths': green_widths,
                'yellow_totals0': yellow_totals0,
                'yellow_totals1': yellow_totals1,
                'yellow_totals2': yellow_totals2,
                'green_totals1': green_totals1,
                'green_totals2': green_totals2,
                'green_totals3': green_totals3,
                'complete': results.skills_complete,
                'started': started,
                'results': results,
                'inventory_page': 1,
    }
    return render_to_response('inventory.html', context=context)


@login_required
def skills_analysis(request):

    try:
        inventory = Inventory.objects.get(type='skills')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'skills_analysis.html',
            context={'error': 'Inventory does not exist.'})

    # get user results
    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=user)
        results.save()

    # load table cell widths
    yellow_widths = {}
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '50px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '90px'
        else:
            yellow_widths[str(ndx)] = '50px'
        ndx=ndx+1
    green_widths = {}
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '80px'
        elif ndx == 1:
            green_widths[str(ndx)] = '100px'
        else:
            green_widths[str(ndx)] = '90px'
        ndx=ndx+1

    # initialize categories
    categories = results.get_top_cats_list(inventory)

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
    answers = Answer.objects.filter(user=request.user, inventory=inventory)
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

    # calculate weighted yellow totals
    yellow_totals = {}
    for category in inventory.categories.all():
        yellow_totals0[category.type] = 0
        yellow_totals1[category.type] = yellow_totals1[category.type]
        yellow_totals2[category.type] = yellow_totals2[category.type]*2
        yellow_totals[category.type] = yellow_totals0[category.type] + yellow_totals1[category.type] + yellow_totals2[category.type]

    # calculate weighted green totals
    green_totals = {}
    for category in inventory.categories.all():
        green_totals1[category.type] = 0
        green_totals2[category.type] = green_totals2[category.type]
        green_totals3[category.type] = green_totals3[category.type]*2
        green_totals[category.type] = green_totals1[category.type] + green_totals2[category.type] + green_totals3[category.type]

    # get interests_areas
    interests_areas = results.get_interests_areas_dict(categories)
    logger.debug(f"interest areas: {str(interests_areas)}")

    # get skills_current
    skills_current = results.get_skills_current_dict(categories)
    logger.debug(f"skills current: {str(skills_current)}")

    # set/get skills_training
    skills_training = results.get_skills_training_dict(categories)
    logger.debug(f"skills training: {str(skills_training)}")

    context = { 'inventory': inventory,
                'categories': categories,
                'yellow_answers': yellow_answers, 
                'green_answers': green_answers, 
                'other_answers': other_answers,
                'yellow_widths': yellow_widths,
                'green_widths': green_widths,
                'yellow_totals0': yellow_totals0,
                'yellow_totals1': yellow_totals1,
                'yellow_totals2': yellow_totals2,
                'yellow_totals': yellow_totals,
                'green_totals1': green_totals1,
                'green_totals2': green_totals2,
                'green_totals3': green_totals3,
                'green_totals': green_totals,
                'interests_areas': interests_areas,
                'skills_current': skills_current,
                'skills_training': skills_training,
                'results': results, 
                'analysis_page': 1,
    }
    return render_to_response('skills_analysis.html', context=context)


@login_required
def skills_summary(request):

    try:
        inventory = Inventory.objects.get(type='skills')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'skills_summary.html',
            context={'error': 'Inventory does not exist.'})

    context = { 'inventory': inventory, 
                'summary_page': 1,
    }
    return render_to_response('skills_summary.html', context=context)


@login_required
def values_inventory(request):

    try:
        inventory = Inventory.objects.get(type='values')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response('inventory.html',
                                  context={'error': error})

    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=request.user)
        results.save()

    # initialize context
    yellow_widths = {}
    green_widths = {}
    yellow_answers = {}
    green_answers = {}
    other_answers = {}
    yellow_totals0 = {}
    yellow_totals1 = {}
    yellow_totals2 = {}
    green_totals1 = {}
    green_totals2 = {}
    green_totals3 = {}
    started = 0
 
    # load yellow_widths
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '40px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '70px'
        else:
            yellow_widths[str(ndx)] = '60px'
        ndx=ndx+1

    # load green_widths
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '40px'
        elif ndx == 1:
            green_widths[str(ndx)] = '70px'
        else:
            green_widths[str(ndx)] = '60px'
        ndx=ndx+1

    # initialize categories
    categories = results.get_top_cats_list(inventory)
    logger.debug(f"values_inventory categories: {str(categories)}")

    posted = 0
    if request.method == 'POST':

        # retrieve user answers and save
        posted = 1
        started = 1
        complete = True
        for category in categories:
            y_totals0 = 0
            y_totals1 = 0
            y_totals2 = 0
            g_totals1 = 0
            g_totals2 = 0
            g_totals3 = 0

            for topic in category.topics.all():
                yellow_id = 'yellow_' + str(topic.id)
                yellow_int = int(request.POST.get(yellow_id, -1))
                green_id = 'green_' + str(topic.id)
                green_int = int(request.POST.get(green_id, -1))
                other_id = 'other_' + str(topic.id)
                other_text = request.POST.get(other_id, '')

                # handle 'Other'
                if topic.name == 'Other':
                    if other_text == '':
                        yellow_int = -1
                        green_int = -1
                    
                # check if answer already exists
                try:
                    answer = Answer.objects.get(user=request.user, topic=topic, inventory=inventory)
                    answer.yellow = yellow_int
                    answer.green = green_int
                    answer.other = other_text
                    answer.save()
                except ObjectDoesNotExist:
                    answer = Answer(yellow=yellow_int, 
                                    green=green_int, 
                                    other=other_text, 
                                    user=request.user, 
                                    topic=topic, 
                                    category=category,
                                    inventory=inventory)
                    answer.save()
                    topic.answers.add(answer)       

                # load user answers in context
                yellow_answers[str(topic.id)] = int(yellow_int)
                green_answers[str(topic.id)] = int(green_int)
                other_answers[str(topic.id)] = other_text
                if yellow_int == -1 and topic.name != 'Other':
                    complete = False
                if yellow_int > 0 and green_int == -1:
                    # answer is incomplete - if no green
                    yellow_answers[str(topic.id)] = -1
                    complete = False

                # compute totals for analysis
                if yellow_int == 0:
                    y_totals0 = y_totals0 + 1
                    yellow_totals0[category.type] = y_totals0
                elif yellow_int == 1:
                    y_totals1 = y_totals1 + 1
                    yellow_totals1[category.type] = y_totals1
                elif yellow_int == 2:
                    y_totals2 = y_totals2 + 1
                    yellow_totals2[category.type] = y_totals2
                if green_int == 1:
                    g_totals1 = g_totals1 + 1
                    green_totals1[category.type] = g_totals1
                elif green_int == 2:
                    g_totals2 = g_totals2 + 1
                    green_totals2[category.type] = g_totals2
                elif green_int == 3:
                    g_totals3 = g_totals3 + 1
                    green_totals3[category.type] = g_totals3

        if complete:
            # perform 'values' analysis
            perform_values_analysis(request.user, inventory, categories, results)
        else:
            results.values_complete = False
            results.save()
        
    else: # request.method == 'GET':

        # load user answers in context
        answers = Answer.objects.filter(user=request.user, inventory=inventory)
        for answer in answers:
            started = 1
            yellow_answers[str(answer.topic.id)] = int(answer.yellow)
            green_answers[str(answer.topic.id)] = int(answer.green)
            other_answers[str(answer.topic.id)] = answer.other
            if int(answer.yellow) > 0 and int(answer.green) == -1:
                # answer is incomplete - if no green
                yellow_answers[str(answer.topic.id)] = -1

            # compute totals for analysis
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

    context = { 'inventory': inventory,
                'categories': categories,
                'yellow_answers': yellow_answers, 
                'green_answers': green_answers, 
                'other_answers': other_answers,
                'yellow_widths': yellow_widths,
                'green_widths': green_widths,
                'yellow_totals0': yellow_totals0,
                'yellow_totals1': yellow_totals1,
                'yellow_totals2': yellow_totals2,
                'green_totals1': green_totals1,
                'green_totals2': green_totals2,
                'green_totals3': green_totals3,
                'complete': results.values_complete,
                'started': started,
                'results': results,
                'inventory_page': 1,
    }

    # if final posting and now complete...
    if posted and results.values_complete:
        return values_analysis(request)

    return render_to_response('inventory.html', context=context)


@login_required
def values_analysis(request):

    try:
        inventory = Inventory.objects.get(type='values')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'values_analysis.html',
            context={'error': 'Inventory does not exist.'})
 
    # get user results
    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=user)
        results.save()

    # load table cell widths
    yellow_widths = {}
    ndx=0
    for choice in inventory.yellow_choices.all():
        if ndx == 0:
            yellow_widths[str(ndx)] = '40px'
        elif ndx == 1:
            yellow_widths[str(ndx)] = '70px'
        else:
            yellow_widths[str(ndx)] = '60px'
        ndx=ndx+1
    green_widths = {}
    ndx=0
    for choice in inventory.green_choices.all():
        if ndx == 0:
            green_widths[str(ndx)] = '40px'
        elif ndx == 1:
            green_widths[str(ndx)] = '70px'
        else:
            green_widths[str(ndx)] = '60px'
        ndx=ndx+1

    # initialize categories
    categories = results.get_top_cats_list(inventory)
    logger.debug(f"values_analysis categories: {categories}")

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
    answers = Answer.objects.filter(user=request.user, inventory=inventory)
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
        yellow_totals[category.type] = yellow_totals0[category.type] + yellow_totals1[category.type] + yellow_totals2[category.type]

    # calculate weighted green totals
    green_totals = {}
    for category in categories:
        green_totals1[category.type] = 0
        green_totals2[category.type] = green_totals2[category.type]
        green_totals3[category.type] = green_totals3[category.type]*2
        green_totals[category.type] = green_totals1[category.type] + green_totals2[category.type] + green_totals3[category.type]

    # get interests_areas
    interests_areas = results.get_interests_areas_dict(categories)
    logger.debug(f"interests_areas: {str(interests_areas)}")

    # get skills_current
    skills_current = results.get_skills_current_dict(categories)
    logger.debug(f"skills_current: {str(skills_current)}")

    # set/get skills_training
    skills_training = results.get_skills_training_dict(categories)
    logger.debug(f"skills_training: {str(skills_training)}")

    # get your_values
    your_values = results.get_your_values_dict(categories)
    logger.debug(f"your_values: {str(your_values)}")

    # get your_values
    job_values = results.get_job_values_dict(categories)
    logger.debug(f"job_values: {str(job_values)}")

    # get top15 values
    your_values_top15_dict = results.get_your_values_top15_dict(categories)
    logger.debug(f"your_values_top15_dict: {str(your_values_top15_dict)}")
    job_values_top15_dict = results.get_job_values_top15_dict(categories)
    logger.debug(f"job_values_top15_dict: {str(job_values_top15_dict)}")

    context = { 'inventory': inventory,
                'categories': categories,
                'yellow_answers': yellow_answers, 
                'green_answers': green_answers, 
                'other_answers': other_answers,
                'yellow_widths': yellow_widths,
                'green_widths': green_widths,
                'yellow_totals0': yellow_totals0,
                'yellow_totals1': yellow_totals1,
                'yellow_totals2': yellow_totals2,
                'yellow_totals': yellow_totals,
                'green_totals1': green_totals1,
                'green_totals2': green_totals2,
                'green_totals3': green_totals3,
                'green_totals': green_totals,
                'interests_areas': interests_areas,
                'skills_current': skills_current,
                'skills_training': skills_training,
                'your_values': your_values,
                'job_values': job_values,
                'your_values_top15_dict': your_values_top15_dict,
                'job_values_top15_dict': job_values_top15_dict,
                'results': results, 
                'analysis_page': 1,
    }
    return render_to_response('values_analysis.html', context=context)

@login_required
def values_summary(request):

    try:
        inventory = Inventory.objects.get(type='values')
    except ObjectDoesNotExist:
        error = 'Inventory does not exist.'
        return render_to_response(
            'inventory.html',
            context={'error': error})

    try:
        results = Results.objects.get(user=request.user)
    except ObjectDoesNotExist:
        results = Results(user=request.user)
        results.save()


    context = { 'inventory': inventory,
                'results': results,
    }
    return render_to_response('values_summary.html', context=context)


@login_required
def certificate(request):

    if request.user.is_authenticated:
        try:
            results = Results.objects.get(user=request.user)
        except ObjectDoesNotExist:
            error = 'Results for this user do not exist.'
            return render_to_response('certificate.html',
                                      context={'error': error})
    completion_date = results.completion_date

    # build this from user.results
    inventory = Inventory.objects.get(type='interests')

    categories = results.get_top_cats_list(inventory)
    category1 = categories[0]
    category2 = categories[1]

    interests_areas = results.get_interests_areas_dict(categories)
    area1 = interests_areas[category1.type]
    area2 = interests_areas[category2.type]
    if area1 == 'Interpersonal':
        area1 = 'Interpersonal issues'
    if area2 == 'Interpersonal':
        area2 = 'Interpersonal issues'

    skills_current = results.get_skills_current_dict(categories)
    current1 = skills_current[category1.type]
    current2 = skills_current[category2.type]

    skills_training = results.get_skills_training_dict(categories)
    skills1 = skills_training[category1.type]
    if skills1 == 'Interested':
        skills1 = 'am Interested in training.'
    elif skills1 == 'Not Interested':
        skills1 = 'am Not Interested in training.'
    else:
        skills1 = 'want training.'
    skills2 = skills_training[category2.type]
    if skills2 == 'Interested':
        skills2 = 'am Interested in training.'
    elif skills2 == 'Not Interested':
        skills2 = 'am Not Interested in training.'
    else:
        skills2 = 'want training.'

    your_values = results.get_your_values_dict(categories)
    yourvalue1 = your_values[category1.type]
    yourvalue2 = your_values[category2.type]

    job_values = results.get_job_values_dict(categories)
    jobvalue1 = job_values[category1.type]
    jobvalue2 = job_values[category2.type]

    wrapup = 'For my future, I am interested in a ' + category1.type + ' career, working principally with\n ' + area1 + \
             '. My current skill level is ' + current1 + ' and I ' + skills1 + ' I am also interested in a ' + category2.type + ' career, ' + \
             ' working principally with ' + area2 + '. My current skill level is ' + current1 + ' and I ' + skills2 + '.'

    context = { 'wrapup': wrapup, 'completion_date': completion_date, }
    return render_to_response('certificate.html', context=context)