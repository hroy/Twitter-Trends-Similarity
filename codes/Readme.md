
#Twitter Trends User Set Similarity

## Install

The project is done in Python and data is saved on MongoDB. So need to install
python and MongoDB.

Install MongoDB in a host and configure the mongo.py with proper hostname and port.

Next configure the twitter_stream.py and yahoo_geoplanet.py with proper keys. For simplicity
our key is provided. Please note that we can't give you life time guarantee of availability of
these keys.

Next run the following two commands. First one inserts available places of twitter trend api.
Second one gets latitudes and longitudes of those places from yahoo geo place api.

    $ python trends.py places insert
    $ python trends.py places lat-long


Next setup a crontab

    */15 * * * * /usr/bin/python  /path/to/trends/trends.py loop > output-redirect-path.log 2>&1


This will make sure that the trend api is called every 15 minutes. On every call it will fetch
 14 place's trending topic and users who tweeted those. and compute similarity matrix


For better performance few index can be added in mongodb. Those are provided in data/mongodb-indexes.txt

Finally to display the result run

    $ python ui.py

It will open a http server at http://localhost:25001/


## Library Used

OAuth2 - to fetch Twitter REST API
urllib - to fetch Twitter and Yahoo GeoPlanet REST API
PyMongo - to query MongoDB database
Flask - for user interface
