from django.shortcuts import render
from main.models import Thread, Post
from django.db.models import Count
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import json

# Create your views here.

# 移除月份內的"0"， 例如：02 --> 2
def remove_zero(string):
    if string[0] == '0':
        return string.replace('0', '')
    return string

# 首頁
def dashboard(request):
    users_num = Post.objects.distinct('author').count()

    negativePost_num = Post.objects.filter(emotion='negative').count()
    positivePost_num = Post.objects.filter(emotion='positive').count()
    neutralPost_num = Post.objects.filter(emotion='neutral').count()

    totalPost_num = negativePost_num + positivePost_num + neutralPost_num

    postivePost_percentage = str(
        (positivePost_num / totalPost_num) * 100) + '%'
    negativePost_percentage = str(
        (negativePost_num / totalPost_num) * 100) + '%'
    neutralPost_percentage = str((neutralPost_num / totalPost_num) * 100) + '%'

    now = date(2015, 12, 31)

    last_12months = sorted([(now - relativedelta(months=m))
                            for m in range(0, 13)])

    postEmotionData = {
        'labels': [m.strftime('%Y %b') for m in last_12months],
        'datasets': [
            {
                #                'label': "正面文章數量",
                'fillColor': "rgb(10, 191, 119)",
                'strokeColor': "rgb(10, 191, 119)",
                'pointColor': "rgb(10, 191, 119)",
                'pointStrokeColor': "#c1c7d1",
                'pointHighlightFill': "#fff",
                'pointHighlightStroke': "rgb(12, 168, 106)",
                'data': [Post.objects.filter(
                    date_time__year=m.strftime('%Y'),
                    date_time__month=remove_zero(m.strftime('%m')),
                    emotion='positive'
                ).count() for m in last_12months]
            },
            {
                #                'label': "負面文章數量",
                'fillColor': "rgb(199, 20, 20)",
                'strokeColor': "rgb(199, 20, 20)",
                'pointColor': "rgb(199, 20, 20)",
                'pointStrokeColor': "rgb(199, 20, 20)",
                'pointHighlightFill': "#fff",
                'pointHighlightStroke': "rgb(199, 20, 20)",
                'data': [Post.objects.filter(
                    date_time__year=m.strftime('%Y'),
                    date_time__month=remove_zero(m.strftime('%m')),
                    emotion='negative'
                ).count() for m in last_12months]
            }
        ]
    }

    return render(
        request, 'dashboard.html',
        {
            'users_num': users_num,
            'negativePost_num': negativePost_num,
            'positivePost_num': positivePost_num,
            'neutralPost_num': neutralPost_num,
            'totalPost_num': totalPost_num,
            'postivePost_percentage': postivePost_percentage,
            'negativePost_percentage': negativePost_percentage,
            'neutralPost_percentage': neutralPost_percentage,
            'postEmotionData': json.dumps(postEmotionData)
        }
    )

# 熱門話題
def hot(request):
    # 為換取網頁載入速度，只選用討論串長度最長的頭500筆資料
    threads = Thread.objects.order_by('-hit')[:500]
    return render(request, 'hot.html', {'threads': threads})

import time

# 名詞關聯分析
# 純粹render模板，
# 圖表資料會由d3.js從/related_words/data.json獲取
def related_words(request):
    return render(request, 'related_words.html')


from django.http import JsonResponse
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import pandas as pd
import multiprocessing
import csv
import io
import os

# 生成/related_words/data.json
def related_words_data(request):

    # 為換取網頁載入速度，只選用2015年12月所有Post為資料來源
    postQuerySet = Post.objects.filter(
        date_time__year='2015', date_time__month='12').values('noun')

    # 過濾無意義字詞
    filtered = ['恕', '人', '後', '時', '樓主', '中']

    # 從QuerySet抽取各個Post內的名詞資料，並製作成list
    wordlist = [[word for word in p['noun'] if word not in filtered]
                for p in postQuerySet]

    # 由於QuerrySet取來的是list格式，要進一步從各個list內抽取文字，並將空白字元過濾
    unpackedWordlist = [w for l in wordlist for w in l if len(w) > 0]

    # 用pandas將list轉換成Series, 並計算每一字的出現次數
    count_dict = pd.Series(unpackedWordlist).value_counts()

    # 只選用出現次數最高的首6個名詞
    words_top6 = list(count_dict[:6].index)

    # 載入從全部10萬資料預先製作的Word2Vec Model
    model = Word2Vec.load_word2vec_format(
        os.path.split(os.path.abspath(__file__))[0] + "/car_posts_nouns.w2v", binary=False)

    # 生成dictionary作為Json的原始資料
    dataset = {
        'name': '',
        'children': [
            {
                'name': x,
                'children': [
                    {
                        'name': y,
                        # count_dict內，pandas使用的數字為int64型態的資料，
                        # 要先轉換成int才能成功生成Json
                        # 將數字×10是為了圖型變更大，更明顯
                        'size': int(count_dict[y]) * 10
                    }
                    # 將出現次數最高的首6個名詞交給model處理，並回傳首5個關聯性最高的名詞，
                    # 由於model的資料來源是全部10筆，而這裡計算的是2015年12月份關聯性最高名詞，
                    # 所以要將model有，但12月份沒有的字詞過濾
                    for y, _ in model.most_similar(x)[0:5] if y in count_dict
                ]
            } for x in words_top6
        ]
    }

    return JsonResponse(dataset, safe=False)

import requests


def leader(request):
    # 若url有GET資料就會讀取該作者的文章資料
    if 'author' in request.GET:
        # 由於作者有可能會在同一個討論串，同一個url的版面回覆數次，
        # 加入distinct把重覆資料刪去
        q = Post.objects.filter(author=request.GET['author']).values(
            'date_time', 'topic', 'url').order_by('url').distinct()

        d = [
            {
                # 將datetime object轉換成string
                'date_time': datetime.strftime(p['date_time'], '%Y-%m-%d %H:%M'),
                'topic': p['topic'],
                'url': p['url'],
            }
            for p in q
        ]

        # 此乃旁門左道，目的是把d轉換成object，方便template讀取資料
        data = json.load(io.StringIO(json.dumps(d)))

        return render(request, 'leader_url.html', {'data': data,
                                                   'author': request.GET['author']}
                      )

    # 若沒有get資料，則從以下url讀取資料，生成最活嚯用戶頁面
    else:
        res = requests.get(request.scheme + '://' +request.META['HTTP_HOST'] + '/leader/data.json')
        obj = io.StringIO(res.text)
        data = json.load(obj)

        return render(request, 'leader.html', {'data': data})

# 生成/leader/data.json
def leader_data(request):

    q = Post.objects.all().values('author')

    dataset = pd.DataFrame.from_records(q)

    # 計算各個作者的出現次數，並取出頭25筆資料
    pd_toplist = dataset['author'].value_counts()[:25]

    top_list_author = pd_toplist.index

    q2 = Post.objects.filter(author__in=top_list_author).values(
        'topic', 'url').order_by('author')

    # 為每位作者計算正面，負面，及中立字詞總量
    emotion_count = []
    for a in top_list_author:
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        qset = Post.objects.filter(author=a).values(
            'positive_words', 'negative_words', 'neutral_words')

        for obj in qset:
            positive_count += len(obj['positive_words'])
            negative_count += len(obj['negative_words'])
            neutral_count += len(obj['neutral_words'])

        emotion_count.append(
            {
                a: {
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'neutral_count': neutral_count,
                }
            }
        )

    # 轉換資料做合適格式，方面最終的dictionary讀取
    tmp_data = [(k, v) for i in emotion_count for k, v in i.items()]
    emotion_dict = {k: v for k, v in tmp_data}

    # 生成dictionary，並轉換成json輸出
    d = [
        {
            'author': i,
            'posts_count': Post.objects.filter(author=i).values('id').count(),
            'emotion': emotion_dict[i]
        }
        for i in top_list_author
    ]

    return JsonResponse(d, safe=False)
