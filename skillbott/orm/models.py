''' Models implementation '''
import logging
import operator

from datetime import date
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from taggit.managers import TaggableManager

logger = logging.getLogger()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    ''' auto create token for new user '''
    if created:
        token, created = Token.objects.get_or_create(user=instance)
        logger.debug("new user token test: "+instance.username+" - "+token.key)


class Inventory(models.Model):
    type = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    tagline = models.TextField(blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    yellow_choices = models.ManyToManyField(
        'Choice', related_name='inventory_yellow_choices',
        blank=True)
    green_choices = models.ManyToManyField(
        'Choice', related_name='inventory_green_choices',
        blank=True)
    categories = models.ManyToManyField(
        'Category', related_name='inventory_categories',
        blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.type, self.id)


class Category(models.Model):
    type = models.CharField(max_length=200)
    hover = models.TextField(blank=True)
    topics = models.ManyToManyField('Topic',
                                    related_name='category_topics',
                                    blank=True)
    inventory = models.ForeignKey('Inventory',
                                  related_name='category_inventory',
                                  on_delete=models.CASCADE,
                                  blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.type, self.id)


class Topic(models.Model):
    name = models.CharField(max_length=200)
    hover = models.TextField(blank=True)
    name2 = models.CharField(max_length=200)
    hover2 = models.TextField(blank=True)
    yellow = models.CharField(max_length=200)
    green = models.CharField(max_length=200)
    answers = models.ManyToManyField('Answer',
                                     related_name='topic_answers',
                                     blank=True)
    category = models.ForeignKey('Category',
                                 related_name='topic_category',
                                 on_delete=models.CASCADE,
                                 blank=True)
    tags = TaggableManager(blank=True)
    
    def __str__(self):
        return u'%s (%s)' % (self.name, self.id)


class Choice(models.Model):
    text = models.CharField(max_length=200)
    hover = models.TextField(blank=True)
    inventory = models.ForeignKey('Inventory',
                                  related_name='choice_inventory',
                                  on_delete=models.CASCADE,
                                  null=True, blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.inventory.type, self.id)


class Answer(models.Model):
    yellow = models.IntegerField(null=True, blank=True, default=-1)
    green = models.IntegerField(null=True, blank=True, default=-1)
    other = models.CharField(max_length=200)
    user = models.ForeignKey(User,
                             related_name='answer_user',
                             on_delete=models.CASCADE,
                             null=True, blank=True)
    topic = models.ForeignKey('Topic',
                              related_name='answer_topic',
                              on_delete=models.CASCADE,
                              null=True, blank=True)
    category = models.ForeignKey('Category',
                                 related_name='answer_category',
                                 on_delete=models.CASCADE,
                                 null=True, blank=True)
    inventory = models.ForeignKey('Inventory',
                                  related_name='answer_inventory',
                                  on_delete=models.CASCADE,
                                  null=True, blank=True)

    def __str__(self):
        return u'%s %s (%s)' % (self.topic.name, self.user.username, self.id)


class Results(models.Model):
    interests_complete = models.BooleanField(default=False)
    skills_complete = models.BooleanField(default=False)
    values_complete = models.BooleanField(default=False)
    completion_date = models.CharField(max_length=200)
    # certificate_number = models.IntegerField(null=True, blank=True,
    #                                          default=0)
    certificate_summary = models.TextField(blank=True)
    top_cats = models.TextField(blank=True, default='')
    
    # assessment table data lists
    interests_areas = models.TextField(blank=True, default='')
    skills_current = models.TextField(blank=True, default='')
    skills_training = models.TextField(blank=True, default='')
    your_values = models.TextField(blank=True, default='')
    job_values = models.TextField(blank=True, default='')
    your_values_top15 = models.TextField(blank=True, default='')
    job_values_top15 = models.TextField(blank=True, default='')
   
    user = models.ForeignKey(User,
                             related_name='results_user',
                             on_delete=models.CASCADE,
                             blank=True)

    def set_completion_date(self):

        # format sample is '21st day of April 2011'    
        today = date.today()
        month = today.strftime('%B')
        year = today.year
        day = today.day

        # determine suffix
        suffix = 'th'
        if day % 20 == 1:
            suffix = 'st'
        elif day % 20 == 2:
            suffix = 'nd'
        elif day % 20 == 3:
            suffix = 'rd'

        # build date string
        self.completion_date = (str(day) + suffix + ' day of ' + 
                                str(month) + ' ' + str(year))

    def set_new_order_top_cats(self, new_order):

        # get current top_cats array and sort
        old_top_cats = self.top_cats.split(',')
        new_top_cats = {}
        ndx = 0
        while ndx < 5:
            new_top_cats[ndx] = str(old_top_cats[int(new_order[ndx])])
            ndx = ndx+1
        ndx = 0
        self.top_cats = ''
        while ndx < 5:
            self.top_cats += str(new_top_cats[ndx]) + ','
            ndx = ndx+1
        self.save()
        return

    def set_top_cats(self, yellow_totals, inventory):

        # sort the categories according to yellow_totals
        categories_dict = {}
        for category in inventory.categories.all():
            categories_dict[category.type] = yellow_totals[category.type]
        categories_dict = sorted(categories_dict.items(),
                                 key=operator.itemgetter(1), reverse=True)

        # build results.top_cat_list
        ndx = 0
        for key, value in categories_dict:
            self.top_cats += key + ','
            ndx = ndx+1
            if ndx == 5:
                break
        self.save()
        return self.get_top_cats_list(inventory)

    def get_top_cats_list(self, inventory):

        top_categories_list = []
        top_cats = self.top_cats.split(',')
        ndx = 0
        while ndx < 5:
            category = inventory.categories.all().get(type=str(top_cats[ndx]))
            top_categories_list.append(category)
            ndx = ndx+1
        return top_categories_list

    def set_interests_areas(self, inventory, categories, green_modes):

        self.interests_areas = ''
        interests_green_choices = {}
        ndx = 0
        for green_choice in inventory.green_choices.all():
            interests_green_choices[ndx] = green_choice.text
            ndx = ndx+1
        mode_choices = {}
        for category in categories:
            mode_choices[category.type] = (interests_green_choices
                                           [green_modes[category.type]-1])
            self.interests_areas += mode_choices[category.type] + ','
        self.save()
        return self.get_interests_areas_dict(categories)

    def get_interests_areas_dict(self, categories):

        interests_areas_dict = {}
        if self.interests_areas != '':
            interests_areas = self.interests_areas.split(',')
            ndx = 0
            for category in categories:
                interests_areas_dict[category.type] = interests_areas[ndx]
                ndx = ndx+1
     
        return interests_areas_dict

    def set_skills_current(self, categories, yellow_totals):

        self.skills_current = ''
        for category in categories:
            if yellow_totals[category.type] < 8:
                self.skills_current += 'Low,'            
            elif yellow_totals[category.type] < 15:
                self.skills_current += 'Medium,'
            else:
                self.skills_current += 'High,'
        self.save()
        return self.get_skills_current_dict(categories)

    def get_skills_current_dict(self, categories):

        skills_current_dict = {}
        if self.skills_current != '':
            skills_current = self.skills_current.split(',')
            ndx = 0
            for category in categories:
                skills_current_dict[category.type] = skills_current[ndx]
                ndx = ndx+1
        return skills_current_dict

    def set_skills_training(self, categories, green_totals):

        self.skills_training = ''
        for category in categories:
            if green_totals[category.type] < 8:
                self.skills_training += 'Not Interested,'
            elif green_totals[category.type] < 15:
                self.skills_training += 'Interested,'
            else:
                self.skills_training += 'Want Training,'
        self.save()
        self.get_skills_training_dict(categories)

    def get_skills_training_dict(self, categories):

        skills_training_dict = {}
        if self.skills_training != '':
            skills_training = self.skills_training.split(',')
            ndx = 0
            for category in categories:
                skills_training_dict[category.type] = skills_training[ndx]
                ndx = ndx+1
        return skills_training_dict

    def set_your_values(self, categories, yellow_totals):

        self.your_values = ''
        for category in categories:
            if yellow_totals[category.type] < 8:
                self.your_values += 'Low,'            
            elif yellow_totals[category.type] < 15:
                self.your_values += 'Medium,'
            else:
                self.your_values += 'High,'
        self.save()
        return self.get_your_values_dict(categories)

    def get_your_values_dict(self, categories):

        your_values_dict = {}
        if self.your_values != '':
            your_values = self.your_values.split(',')
            ndx = 0
            for category in categories:
                your_values_dict[category.type] = your_values[ndx]
                ndx = ndx+1
        return your_values_dict

    def set_job_values(self, categories, green_totals):

        self.job_values = ''
        for category in categories:
            if green_totals[category.type] < 8:
                self.job_values += 'Low,'            
            elif green_totals[category.type] < 15:
                self.job_values += 'Medium,'
            else:
                self.job_values += 'High,'
        self.save()
        return self.get_job_values_dict(categories)

    def get_job_values_dict(self, categories):

        job_values_dict = {}
        if self.job_values != '':
            job_values = self.job_values.split(',')
            ndx = 0
            for category in categories:
                job_values_dict[category.type] = job_values[ndx]
                ndx = ndx+1
        return job_values_dict

    def set_your_values_top15(self, categories, your_values_top3):

        self.your_values_top15 = ''
        for category in categories:
            ndx = 0
            while ndx < 3:
                self.your_values_top15 += (your_values_top3
                                           [category.type][ndx] + ',')
                ndx = ndx+1
        return self.get_your_values_top15_dict(categories)

    def get_your_values_top15_dict(self, categories):

        your_values_top15_dict = {}
        if self.your_values_top15 != '':
            top15 = self.your_values_top15.split(',')
            ndx15 = 0
            for category in categories:
                your_values_top15_dict[category.type] = {}
                ndx = 0
                while ndx < 3:
                    your_values_top15_dict[category.type][ndx] = top15[ndx15]
                    ndx = ndx+1
                    ndx15 = ndx15+1
        return your_values_top15_dict

    def set_job_values_top15(self, categories, job_values_top3):

        self.job_values_top15 = ''
        for category in categories:
            ndx = 0
            while ndx < 3:
                self.job_values_top15 += (job_values_top3
                                          [category.type][ndx] + ',')
                ndx = ndx+1
        return self.get_job_values_top15_dict(categories)

    def get_job_values_top15_dict(self, categories):

        job_values_top15_dict = {}
        if self.job_values_top15 != '':
            top15 = self.job_values_top15.split(',')
            ndx15 = 0
            for category in categories:
                job_values_top15_dict[category.type] = {}
                ndx = 0
                while ndx < 3:
                    job_values_top15_dict[category.type][ndx] = top15[ndx15]
                    ndx = ndx+1
                    ndx15 = ndx15+1
        return job_values_top15_dict

    def __str__(self):
        return u'%s (%s)' % (self.user.username, self.id)


class Customer(models.Model):
    name = models.CharField(max_length=64)
    access_code = models.CharField(max_length=64)
    url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    users = models.ManyToManyField(User, related_name='customer_users',
                                   blank=True)
    profile = models.TextField(null=True, blank=True)

    def __str__(self):
        return u'%s (%s)' % (self.name, self.id)
