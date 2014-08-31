import urllib
import urllib2
import json

yahoo_app_id = 'dd4752rV34FVKLPC8XHP_E6JfRRJrQSD_f_ELDBvburz9Rzq1B9kDwLeuXygAvKfVDk-'


def find_woeid_details(woeid):
    values = {'appid': yahoo_app_id, 'format': 'json'}
    data = urllib.urlencode(values)

    url = 'http://where.yahooapis.com/v1/place/%s?%s' % (woeid, data)
    req = urllib2.Request(url)

    try:
        response = urllib2.urlopen(req)
        the_page = response.read()

        return the_page
    except urllib2.HTTPError as e:
        print e.code
        print e.read()
        return None


if __name__ == '__main__':
    print "Details for Dallas Ft. Worth"
    place = 2388929
    result = json.loads(find_woeid_details(place))
    print json.dumps(result, indent=4)
