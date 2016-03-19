import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'site02.settings'

import django
django.setup()

from main.models import Thread, Post

from tqdm import tqdm
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing
import csv
import io


postQuerrySet = Post.objects.all()

filtered = ['恕', '人', '後', '時', '樓主']

print('Generating word list ...')
wordlist = [[word for word in p.noun if word not in filtered]
            for p in tqdm(postQuerrySet, total=postQuerrySet.count())]

print('Preparing file object to be feeded to Word2Vec ...')
wordlist_line = ''
for words in tqdm(wordlist):
    wordlist_line += ' '.join(words) + '\n'

f = io.StringIO(wordlist_line)

print('Generating Word2Vec Model ...')
model = Word2Vec(LineSentence(f), size=400, window=5, min_count=5,
                 workers=multiprocessing.cpu_count())

model.save_word2vec_format('car_posts_nouns.bin', binary=True)

print('Finished!')
