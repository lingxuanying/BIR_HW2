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
uploaded_file_url = ''

# Create your views here.
def index(request):
    return render(request, "index.html") #必须用这个return

# POST
@csrf_exempt
def show_post(request):
    if 'ok' in request.POST:
        search_text = request.POST['search_text']
        global uploaded_file_url
        print(uploaded_file_url)
        print(search_text)
        count = 0
        if (uploaded_file_url[len(uploaded_file_url) - 4:] == '.xml'):
            tree = ET.parse(uploaded_file_url[1:])
            root = tree.getroot()

            all_text = []
            title = ''
            for article in root.iter('Article'):
                characters = 0
                words = 0
                sentences = 0
                text = []
                for title in article.iter('ArticleTitle'):
                    title = title.text
                for abstract in article.iter('Abstract'):
                    for t in abstract.iter('AbstractText'):
                        try:
                            text.append(t.attrib['Label'])
                        except:
                            text.append('')
                        text.append(t.text.replace(search_text, "<mark>"+search_text+"</mark>"))
                        count = count + t.text.count(search_text)
                        # calculate the characters, words, sentences
                        for i in t.text:
                            if ord(i) > 32 and ord(i) != 127:
                                characters = characters + 1
                        word_list = t.text.split()
                        words = words + len(word_list)
                        sentences = sentences + len(sent_tokenize(t.text))
                all_text.append({'title': title, 'text': text, 'characters': characters, 'words': words,
                                 'sentences': sentences})  # [title, [label, text]*n]
            return render(request, "result.html", {'all_text': all_text, 'count': count})
        else:
            all_text = []
            json_data = open(os.path.join(settings.BASE_DIR, uploaded_file_url[1:]), "r", encoding="utf-8")
            data1 = json.load(json_data)  # deserialises it
            for i in data1:
                characters = 0
                words = 0
                sentences = 0

                for j in i["tweet_text"]:
                    if ord(j) > 32 and ord(j) != 127:
                        characters = characters + 1
                word_list = i["tweet_text"].split()
                words = words + len(word_list)
                sentences = sentences + len(sent_tokenize(i["tweet_text"]))
                count = count + i["tweet_text"].count(search_text)
                all_text.append(
                    {'username': i["username"], 'text': i["tweet_text"].replace(search_text, "<mark>" + search_text + "</mark>")
                     , 'characters': characters, 'words': words, 'sentences': sentences})

            return render(request, "result2.html", {'all_text': all_text, 'count': count})


def handle_xml_upload(request):
    if request.method == 'POST' and request.FILES['xmlfile']:
        xmlfile = request.FILES['xmlfile']
        fs = FileSystemStorage()
        filename = fs.save(xmlfile.name, xmlfile)
        global uploaded_file_url
        uploaded_file_url = fs.url(filename)
        count = 0
        if(uploaded_file_url[len(uploaded_file_url)-4:]=='.xml'):
            #file = open(os.path.join(settings.BASE_DIR, uploaded_file_url))
            tree = ET.parse(uploaded_file_url[1:])
            root = tree.getroot()

            all_text = []
            numbers = []
            title = ''
            for article in root.iter('Article'):
                characters = 0
                words = 0
                sentences = 0
                text = []
                for title in article.iter('ArticleTitle'):
                    title = title.text
                for abstract in article.iter('Abstract'):
                    for t in abstract.iter('AbstractText'):
                        try:
                            text.append(t.attrib['Label'])
                        except:
                            text.append('')
                        text.append(t.text)

                        # calculate the characters, words, sentences
                        for i in t.text:
                            if ord(i)>32 and ord(i)!=127:
                                characters = characters + 1
                        word_list = t.text.split()
                        words = words + len(word_list)
                        sentences = sentences + len(sent_tokenize(t.text))
                all_text.append({'title': title, 'text': text, 'characters': characters, 'words': words, 'sentences': sentences}) # [title, [label, text]*n]
            return render(request, "result.html", {'all_text': all_text})
        else:
            all_text = []
            numbers = []
            json_data = open(os.path.join(settings.BASE_DIR, uploaded_file_url[1:]), "r", encoding="utf-8")
            data1 = json.load(json_data)  # deserialises it
            for i in data1:
                characters = 0
                words = 0
                sentences = 0

                for j in i["tweet_text"]:
                    if ord(j) > 32 and ord(j) != 127:
                        characters = characters + 1
                word_list = i["tweet_text"].split()
                words = words + len(word_list)
                sentences = sentences + len(sent_tokenize(i["tweet_text"]))
                all_text.append({'username': i["username"], 'text': i["tweet_text"], 'characters': characters, 'words': words,
                     'sentences': sentences})

            return render(request, "result2.html", {'all_text': all_text})


