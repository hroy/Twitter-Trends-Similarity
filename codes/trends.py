from twitter_stream import *
from yahoo_geoplanet import *
from mongo import *
import time
import datetime
import json
import sys
import os


def project_dir():
    return os.path.dirname(os.path.realpath(__file__))


def page_number_file():
    return project_dir() + '/data/page_count.txt'


def fetch_available_places():
    url = 'https://api.twitter.com/1.1/trends/available.json'
    response = twitter_req(url, 'GET', [])
    result = ""
    for line in response:
        result += line.strip()

    return result


def fetch_trends(woeid):
    url = 'https://api.twitter.com/1.1/trends/place.json'
    response = twitter_req(url, 'GET', {'id': woeid})
    result = ""
    for line in response:
        result += line.strip()

    return result


def fetch_top_results(query, geocode, count=100, lang='en'):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    response = twitter_req(url, 'GET', {'q': query, 'geocode': geocode, 'lang': lang, 'count': count})
    result = ""
    for line in response:
        result += line.strip()

    return result


def update_lat_long():
    for place in read_places():
        details = json.loads(find_woeid_details(place['woeid']))
        latitude = details['place']['centroid']['latitude']
        longitude = details['place']['centroid']['longitude']

        print "Updating: %s, Latitude: %s, Longitude: %s" % (place['woeid'], latitude, longitude)

        update_latitude_longitude(woeid=place['woeid'],
                                  latitude=latitude,
                                  longitude=longitude)


def next_page(page_number):
    return (page_number + 1) % 5


def current_page():
    page_number = open(page_number_file()).read().strip()
    if not page_number or page_number == "":
        return 0

    return int(page_number)


def save_page(page_number):
    open(page_number_file(), 'w').write(str(page_number))


def fetch_trend_users(place_trend_data):
    place_woeid = place_trend_data['woeid']
    place_details = read_place_by_woeid(place_woeid)

    geocode = "%s,%s,%smi" % (place_details['latitude'], place_details['longitude'], 10)
    trend_time = place_trend_data['created_at']

    for trend_topics in place_trend_data['trends']:

        tweets = json.loads(fetch_top_results(trend_topics['query'], geocode))
        if 'errors' in tweets and tweets['errors'][0]['code'] == 88:
            print "Rate limit exceeded for search/tweets"
            break

        topic = trend_topics['name']

        print "Querying topic: %s" % topic

        users = []
        for u in tweets['statuses']:
            user = {'name': u['user']['name'],
                    'screen_name': u['user']['screen_name'],
                    'id': u['user']['id']}
            users.append(user)

        insert_trend_user(trend_time=trend_time, topic=topic, users=users)


def fetch_location_trends():
    page = current_page()

    for place in read_places_page('US', page):

        print "Reading trends of %s - %s " % (place['woeid'], place['name'])
        result = json.loads(fetch_trends(place['woeid']))

        if 'errors' in result and result['errors'][0]['code'] == 88:
            print "Rate limit exceeded for trends/place api"
            break

        insert_trends(result)
        fetch_trend_users(result[0])

    print "Saving next page number"
    save_page(next_page(page))


if __name__ == '__main__':

    dallas = 2388929

    if sys.argv[1] == 'places' and sys.argv[2] == 'insert':
        result = json.loads(fetch_available_places())
        insert_places(result)

    elif sys.argv[1] == 'places' and sys.argv[2] == 'view-us':

        page = current_page()
        for p in read_places_page('US', page):
            print "%s - %s " % (p['woeid'], p['name'])

        print "Saving next page number"
        save_page(next_page(page))

    elif sys.argv[1] == 'places' and sys.argv[2] == 'lat-long':

        update_lat_long()

    elif sys.argv[1] == 'trend':

        place = dallas
        result = json.loads(fetch_trends(place))
        insert_trends(result)

    elif sys.argv[1] == 'loop':

        print 'Fetching Location trend'
        fetch_location_trends()

        print 'Creating similarity matrix'
        generate_similarity()


    elif sys.argv[1] == 'topic-user':

        generate_topic_users()

    elif sys.argv[1] == 'similarity':

        print 'Creating similarity matrix'
        generate_similarity()

    else:
        print 'Invalid arguments'
