# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-11 01:42
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('author', models.CharField(max_length=100)),
                ('topic', models.TextField()),
                ('content', models.TextField()),
                ('emotion', models.CharField(max_length=10)),
                ('url', models.URLField()),
                ('adj', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), size=None)),
                ('noun', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('topic', models.TextField()),
                ('author', models.CharField(max_length=100)),
                ('hit', models.IntegerField()),
                ('emotion', models.CharField(max_length=10)),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Thread'),
        ),
    ]