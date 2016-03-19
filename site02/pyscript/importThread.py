#!/usr/bin/env python3.4

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'site02.settings'

import django
django.setup()

from main.models import Thread, Post
from datetime import datetime
from pytz import timezone
from tqdm import tqdm

import csv

#with open('raw/head10000.csv', 'r') as csvfile:
with open('raw/mobile01-luxgen-2013-15_uniq_with_adj_n.csv', 'r') as csvfile:
    csv_reader = csv.reader(csvfile)

    print('Generating Topic List ...')

    topicList, dataset = [], []

    #for row in tqdm(csv_reader, total=10000):
    for row in tqdm(csv_reader, total=102874):
        if row[2] not in topicList:
            topicList.append(row[2])

        dataset.append({
            'date_time': datetime.strptime(
                row[0].strip(), '%Y-%m-%d %H:%M').replace(
                tzinfo=timezone('Asia/Taipei')),
            'author': row[1],
            'topic': row[2],
            'url': row[6].strip(),
        })

    print('topicList:', len(topicList))
    print('dataset:', len(dataset))

print('Grouping records by topic ...')

groupby_topic = [
    {
        'topic': topic,
        'posts': [
            {
                'url': i['url'],
                'date_time': i['date_time'],
                'author': i['author'],
            }
            for i in dataset if i['topic'] == topic
        ]
    } for topic in tqdm(topicList)
]

print('groupby_topic:', len(groupby_topic))

print('Generating Thread Records ...')
thread_record = [
    {
        'topic': topic['topic'],
        'date_time': topic['posts'][0]['date_time'],
        'url': topic['posts'][0]['url'],
        'hit': len(topic['posts']),
        'author': topic['posts'][0]['author']
    } for topic in tqdm(groupby_topic)
]

print('thread_record:', len(thread_record))

print('Importing Thread objects ...')
for i in tqdm(thread_record):
    if '&p=' in i['url']:
        url = i['url'][:i['url'].index('&p=')]
    else:
        url = i['url']
    Thread.objects.create(date_time=i['date_time'],
                          topic=i['topic'].strip(),
                          author=i['author'].strip(),
                          hit=i['hit'],
                          emotion='TBC',
                          url=url)

t_obj_len = Thread.objects.all().count()

print(t_obj_len, 'Thread objects have been imported!')
