# Generated by Django 2.1.4 on 2018-12-23 04:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yellow', models.IntegerField(blank=True, default=-1, null=True)),
                ('green', models.IntegerField(blank=True, default=-1, null=True)),
                ('other', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=200)),
                ('hover', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('hover', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('tagline', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('instructions', models.TextField(blank=True)),
                ('categories', models.ManyToManyField(blank=True, related_name='inventory_categories', to='orm.Category')),
                ('green_choices', models.ManyToManyField(blank=True, related_name='inventory_green_choices', to='orm.Choice')),
                ('yellow_choices', models.ManyToManyField(blank=True, related_name='inventory_yellow_choices', to='orm.Choice')),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interests_complete', models.BooleanField(default=False)),
                ('skills_complete', models.BooleanField(default=False)),
                ('values_complete', models.BooleanField(default=False)),
                ('completion_date', models.CharField(max_length=200)),
                ('certificate_summary', models.TextField(blank=True)),
                ('top_cats', models.TextField(blank=True, default='')),
                ('interests_areas', models.TextField(blank=True, default='')),
                ('skills_current', models.TextField(blank=True, default='')),
                ('skills_training', models.TextField(blank=True, default='')),
                ('your_values', models.TextField(blank=True, default='')),
                ('job_values', models.TextField(blank=True, default='')),
                ('your_values_top15', models.TextField(blank=True, default='')),
                ('job_values_top15', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('hover', models.TextField(blank=True)),
                ('name2', models.CharField(max_length=200)),
                ('hover2', models.TextField(blank=True)),
                ('yellow', models.CharField(max_length=200)),
                ('green', models.CharField(max_length=200)),
                ('answers', models.ManyToManyField(blank=True, related_name='topic_answers', to='orm.Answer')),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='topic_category', to='orm.Category')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.AddField(
            model_name='choice',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='choice_inventory', to='orm.Inventory'),
        ),
        migrations.AddField(
            model_name='category',
            name='inventory',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_inventory', to='orm.Inventory'),
        ),
        migrations.AddField(
            model_name='category',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='category_topics', to='orm.Topic'),
        ),
        migrations.AddField(
            model_name='answer',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_category', to='orm.Category'),
        ),
        migrations.AddField(
            model_name='answer',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_inventory', to='orm.Inventory'),
        ),
        migrations.AddField(
            model_name='answer',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_topic', to='orm.Topic'),
        ),
        migrations.AddField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
