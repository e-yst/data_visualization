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

print('Importing Post objects ...')
with open('raw/mobile01-luxgen-2013-15_uniq_with_adj_n.csv', 'r') as inpfile:
    reader = csv.reader(inpfile)

    for row in tqdm(reader, total=102874):

        date_time = datetime.strptime(
            row[0].strip(), '%Y-%m-%d %H:%M').replace(
            tzinfo=timezone('Asia/Taipei'))

        author = row[1].strip()

        topic = row[2].strip()

        content = row[3].strip()

        adj = [w for w in row[4].split(' ') if len(w) != 0]

        noun = [w for w in row[5].split(' ') if len(w) != 0]

        url = row[6]

        try:
            thread = Thread.objects.get(topic=topic)
        except:
            print('===== Somethings Wrong HERE! =====')
            print(topic)
            break

        wordList = [w for w in row[4].split(' ') if len(w) != 0]
        wordList.extend([w for w in row[5].split(' ') if len(w) != 0])

        posCounter, negCounter, neutralCounter = 0, 0, 0
        for i in wordList:
            if i in positiveList:
                posCounter += 1
            elif i in negativeList:
                negCounter += 1
            else:
                neutralCounter += 1

        if (neutralCounter > posCounter) and (neutralCounter> negCounter):
            emotion = 'neutral'
        elif (posCounter == negCounter):
            emotion = 'neutral'

        elif (posCounter > negCounter) and (posCounter >= neutralCounter):
            emotion = 'positive'

        elif (negCounter > posCounter) and (negCounter >= neutralCounter):
            emotion = 'negative'

        else:
            print('===== Somethings Wrong HERE! =====' + '\n' +
                  'topic:', topic + '\n' +
                  'positive:', str(posCounter) + '\n'
                  'negative:', str(negCounter) + '\n'
                  'neutral:', str(neutralCounter))
            break

        post=Post.objects.create(date_time=date_time, author=author, topic=topic,
            content=content, adj=adj, noun=noun, emotion=emotion, url=url, thread=thread)

p_obj_len=Post.objects.all().count()

print(p_obj_len, 'Post objects have been imported!')
