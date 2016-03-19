import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'site02.settings'

import django
django.setup()

from main.models import Thread, Post
from datetime import datetime
from pytz import timezone
from tqdm import tqdm

print("Calculating Threads' emotions ...")
for thread in tqdm(Thread.objects.all()):
    post_q = Post.objects.filter(topic=thread.topic)

    count_dict = {
        'positive': 0,
        'negative': 0,
        'neutral': 0
    }

    for post in post_q:
        if post.emotion == 'positive':
            count_dict['positive'] += 1
        elif post.emotion == 'negative':
            count_dict['negative'] += 1
        elif post.emotion == 'neutral':
            count_dict['neutral'] += 1
        else:
            print('WTF?')

    if (count_dict['neutral'] > count_dict['positive']) and (count_dict['neutral']> count_dict['negative']):
        thread_emotion = 'neutral'
    elif (count_dict['positive'] == count_dict['negative']):
        thread_emotion = 'neutral'

    elif (count_dict['positive'] > count_dict['negative']) and (count_dict['positive'] >= count_dict['neutral']):
        thread_emotion = 'positive'

    elif (count_dict['negative'] > count_dict['positive']) and (count_dict['negative'] >= count_dict['neutral']):
        thread_emotion = 'negative'

    else:
        print('===== Somethings Wrong HERE! =====' + '\n' +
              'topic:', topic + '\n' +
              'positive:', str(count_dict['positive']) + '\n'
              'negative:', str(count_dict['negative']) + '\n'
              'neutral:', str(count_dict['neutral']))
        break

    thread.emotion = thread_emotion
    thread.save()

print('All Threads have been updated!')
