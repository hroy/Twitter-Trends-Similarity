import json
import sys
import os
import urllib
import random
from mongo import *

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, Response

app = Flask(__name__)


@app.route('/place')
def place():
    woeid = int(request.args['woeid'])
    place = read_place_by_woeid(woeid)
    return render_template('place.html', place=place, trends=read_trends(woeid))


@app.route('/similarity')
def similarity():
    topics = []
    for arg in request.args:
        if arg.startswith('topic_'):
            topics.append(request.args[arg].strip())

    rand_selection = 0
    if len(topics) == 0:
        rand_selection = 1
        topics = random.sample(set(find_distinct_topics()), 5)

    topics = sorted(topics)
    return render_template('similarity.html', topics=topics, similarity=find_similarity_matrix(topics),
                           rand_selection=rand_selection)


@app.route('/distinct')
def distinct():
    return render_template('distinct.html', topics=find_distinct_topics())


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
def home():
    return render_template('home.html', places=read_places_by_country_code('US'))


@app.context_processor
def utility_processor():
    def length(a):
        return len(a)

    return dict(length=length)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=25001)
