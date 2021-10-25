from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import xml.etree.ElementTree as ET
from django.core.files.storage import FileSystemStorage
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import json
import os
from django.conf import settings
import re
from search import models
from django.core.paginator import Paginator
from nltk.stem import PorterStemmer


uploaded_file_url = ''

# Create your views here.
def index(request):
    return render(request, "index.html") #必须用这个return

def minDistance(word1: str, word2: str) -> int:
    len1, len2 = len(word1), len(word2)
    # Initialization
    dp = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    # Iteration
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
    #print(word1, word2, dp[len1][len2])
    return dp[len1][len2]

def similarity(word1: str, word2: str) -> int:
    len1, len2 = len(word1), len(word2)
    # Initialization
    count = 0
    for i in range(1, min(len1+1, len2+1)):
        if(word1[i-1] == word2[i-1]):
            count = count+1
        else:
            break

    return len1 - count
def search(request, text):
    ps = PorterStemmer()
    search_text = ps.stem(text)

    # spell correction top 5
    spell_c = [['a', 8000], ['a', 8000], ['a', 8000], ['a', 8000], ['a', 8000]]
    index_field = list(models.WordDictionary.objects.values_list('index_field'))

    #print(index_field)
    for i in index_field:
        temp = minDistance(search_text,i[0]) + similarity(search_text,i[0])
        if (temp < spell_c[4][1]):
            exist = False
            for j in range(5):
                if (spell_c[j][0] == i[0]):
                    exist = True
                    break;
            if (not exist):
                spell_c[4][1] = temp
                spell_c[4][0] = i[0]
                exist = True
            spell_c = sorted(spell_c, key=lambda l: l[1], reverse=False)

    all_text = []
    title = ''
    text = []

    #try:
    index_list = models.WordDictionary.objects.filter(index_field=search_text)
    count = 0
    #print(search_text)
    if(len(index_list)>0 and len(search_text)>0):
        index_list_pair = index_list[0].value_field # [[article_id, title/abstract, location]]
        index_list_pair = eval(index_list_pair)
        count = len(index_list_pair)
        #print(index_list_pair)
        article_id = []
        for i in index_list_pair:
            article_id.append(i[0])
        #print(article_id)

        article_id = set(article_id)
        articles = models.RawText.objects.filter(index_field__in=article_id)
        paginator = Paginator(articles, 10)  # Show 10 contacts per page
        page = request.GET.get('page')
        contacts = paginator.get_page(page)

        for i in range(len(contacts)):
            if(len(contacts[i].abstract)>0 or len(contacts[i].title)>0 ):
                title = contacts[i].title.split()
                word = contacts[i].abstract.split()
                for j in index_list_pair:
                    #print(j)
                    #print(articles[i].index_field, j[0])
                    if (str(j[0]) == str(contacts[i].index_field)) and (j[1] == 1) and len(word) > j[2]:
                        word[j[2]] = "<mark>"+word[j[2]]+"</mark>"
                    elif (str(j[0]) == str(contacts[i].index_field)) and (j[1] == 0) and len(title) > j[2]:
                        title[j[2]] = "<mark>" + title[j[2]] + "</mark>"


                contacts[i].abstract = ' '.join(word)
                contacts[i].title = ' '.join(title)
            #print(' '.join(word))


    else:
        return render(request, "result.html", {'spell_c': spell_c, 'all_text': all_text, 'count': count})
    return render(request, "result.html", {'contacts': contacts, 'spell_c': spell_c, 'all_text': all_text, 'count': count})

# Create your views here.
def statistics(request):
    return render(request, "statistics.html") #必须用这个return



