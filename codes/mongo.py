from pymongo import MongoClient
import json

client = MongoClient('localhost', 27017)
db = client['twitter']


def insert_places(places):
    print "Inserting %s available places." % len(places)

    for p in places:
        p['_id'] = p['woeid']
        db.places.insert(p)


def read_places_by_country_code(country_code):
    places = []
    for p in db.places.find({'countryCode': country_code}).sort('woeid', 1):
        places.append(p)

    return places


def read_places_page(country_code, page_number):
    places = []
    page_size = 14
    cur = db.places.find({'countryCode': country_code}).sort('woeid', 1) \
        .skip(page_number * page_size).limit(page_size)

    for p in cur:
        places.append(p)

    return places


def read_place_by_woeid(woeid):
    return db.places.find_one({'_id': woeid})


def read_places():
    places = []
    for p in db.places.find():
        places.append(p)

    return places


def update_latitude_longitude(woeid, latitude, longitude):
    db.places.update({'_id': woeid}, {'$set': {'latitude': latitude, 'longitude': longitude}})


def insert_trends(trends_data):
    if isinstance(trends_data, list):
        trends_data = trends_data[0]

    trends_data['woeid'] = trends_data['locations'][0]['woeid']
    db.trends.insert(trends_data)


def read_trends(woeid):
    trends = []
    for t in db.trends.find({'woeid': woeid}):
        trends.append(t)

    return trends


def find_trends(query):
    trends = []
    for t in db.trends.find(query):
        trends.append(t)

    return trends


def insert_trend_user(trend_time, topic, users):
    trend_user = {'trend_time': trend_time, 'topic': topic, 'users': users}
    db.trend_users.insert(trend_user)
    add_topic_users(trend_user)


def find_trend_user(trend_time, topic):
    return db.trend_users.findOne({'trend_time': trend_time, 'topic': topic})


def add_topic_users(trend_user):
    if db.topic_users.find_one({'topic': trend_user['topic']}) is None:
        db.topic_users.insert({'topic': trend_user['topic'], 'users': trend_user['users']})
    else:
        db.topic_users.update({'topic': trend_user['topic']}, {'$addToSet': {'users': {'$each': trend_user['users']}}})


def generate_topic_users():
    cur = db.trend_users.find()

    for trend_user in cur:
        if db.topic_users.find_one({'topic': trend_user['topic']}) is None:
            db.topic_users.insert({'topic': trend_user['topic'], 'users': trend_user['users']})
        else:
            db.topic_users.update({'topic': trend_user['topic']},
                                  {'$addToSet': {'users': {'$each': trend_user['users']}}})


def find_distinct_topics():
    return db.topic_users.distinct('topic')


def generate_similarity():
    cur1 = db.topic_users.find().sort('topic', 1)

    for topic1 in cur1:
        cur2 = db.topic_users.find().sort('topic', 1)
        topic1_user_set = set()

        for u in topic1['users']:
            topic1_user_set.add(u['id'])

        t1 = topic1['topic']
        for topic2 in cur2:
            t2 = topic2['topic']
            print "%s - %s " % (t1, t2)

            topic2_user_set = set()
            for u in topic2['users']:
                topic2_user_set.add(u['id'])

            intersection = topic1_user_set.intersection(topic2_user_set)
            union = topic1_user_set.union(topic2_user_set)

            if len(union) == 0:             # both are empty set
                jaccard_similarity = 0.0
            elif t1 == t2:
                jaccard_similarity = 1.0
            else:
                jaccard_similarity = float(len(intersection)) / float(len(union))

            s = db.similarity.find_one({'topic1': t1, 'topic2': t2})
            if s is None:
            # not inserted yet
                db.similarity.insert({'topic1': t1, 'topic2': t2, 'jaccard': jaccard_similarity})
            else:
                db.similarity.update({'topic1': t1, 'topic2': t2}, {'$set': {'jaccard': jaccard_similarity}})


def find_similarity_matrix(topics):
    result_matrix = []
    for t1 in topics:
        row = []
        for t2 in topics:
            s = db.similarity.find_one({'topic1': t1, 'topic2': t2})
            if s is None:
                row.append(0.0)
            else:
                row.append(s['jaccard'])

        result_matrix.append(row)

    return result_matrix
