import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'site02.settings'

import django
django.setup()

from main.models import Thread, Post
from datetime import datetime
from pytz import timezone
from tqdm import tqdm

import csv

with open('raw/NTUSD_all.txt', 'r') as inpfile:
    reader = csv.reader(inpfile)

    positiveList, negativeList = [], []
    for i in reader:
        if i[1] == 'positive':
            positiveList.append(i[0])
        elif i[1] == 'negative':
            negativeList.append(i[0])

print('Updating Post objects ...')
with open('raw/mobile01-luxgen-2013-15_uniq_with_adj_n.csv', 'r') as inpfile:
    reader = csv.reader(inpfile)

    for p in tqdm(Post.objects.all(), total=Post.objects.all().count()):
        all_word = [i for i in p.adj]
        all_word.extend([i for i in p.noun])

        negative_words = [w for w in all_word if w in negativeList]
        positive_words = [w for w in all_word if w in positiveList]
        neutral_words = [
            w for w in all_word if w not in positive_words and w not in negative_words]

        p.positive_words = positive_words
        p.negative_words = negative_words
        p.neutral_words = neutral_words

        try:
            p.save()
        except:
            print('===== Somethings Wrong HERE! =====' + '\n' +
                  'topic', p.topic + '\n' +
                  'url', p.url)
            break

print('All Posts have been updated!')
