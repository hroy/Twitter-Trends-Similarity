import oauth2 as oauth
import urllib2 as urllib

# User specific
access_token_key = "24106081-aQsvqZ0Qh8bvi5XFGZD0mmzKvhZKMaUIkCVxdSghP"
access_token_secret = "6badkpWXDuo4Qsbyb7zfQfjLersFFTmh2OFv3XCYfOcjS"

# Application specific by developer
consumer_key = "V1ut0mpuJYhdm9jIzLoL1w"
consumer_secret = "UBw3sC2krAtRLdIjW6HeEUH38QRT5d6glB32Y981o"

_debug = 0

oauth_token = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

# http_method = "GET"

http_handler = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''


def twitter_req(url, http_method, parameters):
    req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                                token=oauth_token,
                                                http_method=http_method,
                                                http_url=url,
                                                parameters=parameters)

    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

    headers = req.to_header()

    if http_method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
        url = req.to_url()

    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    response = opener.open(url, encoded_post_data)
    return response


def fetch_samples():
    url = "https://stream.twitter.com/1/statuses/sample.json"
    parameters = []
    response = twitter_req(url, "GET", parameters)
    for line in response:
        print line.strip()


if __name__ == '__main__':
    fetch_samples()

