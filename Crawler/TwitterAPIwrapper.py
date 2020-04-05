import oauth2 as oauth
import tldextract
import re


base_url = 'https://api.twitter.com/'

# Describe how to form a query !!!
rate_endpoint = '1.1/application/rate_limit_status.json'

url_encode = {' ': '%20',
              '!': '%21',
              '"': '%22',
              '#': '%23',
              '$': '%24',
              '%': '%25',
              '&': '%26',
              "'": '%27',
              '(': '%28',
              ')': '%29',
              '*': '%2A',
              '+': '%2B',
              ',': '%2C',
              '/': '%2F',
              ':': '%3A',
              ';': '%3B',
              '=': '%3D',
              '?': '%3F',
              '@': '%40',
              '[': '%5B',
              ']': '%5D'
              }


class SearchTwitter:

    def __init__(self, auth):
        self.access_token = auth['access_token']
        self.access_token_secret = auth['access_token_secret']
        self.consumer_key = auth['consumer_key']
        self.consumer_secret = auth['consumer_secret']

        self.consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        self.token = oauth.Token(key=self.access_token, secret=self.access_token_secret)
        self.client = oauth.Client(self.consumer, self.token)

    @staticmethod
    def build_query(endpoint, params):
        try:
            query = params.pop('q')
            encoded_query = '?q='
            for i in query:
                char = url_encode.get(i)
                if char is not None:
                    encoded_query += char
                else:
                    encoded_query += i
        except KeyError:
            encoded_query = '?'
            counter = 0
            for arg in params:
                encoded_query += (arg + '=' + str(params[arg]))
                if counter < len(params) - 1:
                    encoded_query += '&'
                counter += 1
            print(base_url + endpoint + encoded_query)
            return base_url + endpoint + encoded_query

        for arg in params:
            encoded_query += ('&' + arg + '=' + params[arg])
        print(base_url + endpoint + encoded_query)
        return base_url + endpoint + encoded_query
    # Move the url methods to main program ?
    @staticmethod
    def find_url(text):
        urls = re.findall(r'(https?://\S+)', text)
        return urls

    def inspect_url(self, tweet):
        urls = self.find_url(tweet)
        ext = {}
        count = 0
        for url in urls:
            count += 1
            ext[count] = tldextract.extract(url)

        return ext

    def get_limits(self, resources):

        query = base_url + rate_endpoint + '?resources='
        for i in resources:
            query += i
        resp, data = self.client.request(query)
        print(resp)

        return data

    def search(self, endpoint, **kwargs):
        """Allowed params: endpoint, q='query', geocode='lat,long,radius', lang='language', locale='query lang',
         result_type='either mixed, recent or popular', count='results per page, max 100 def 15, until='date till',
         since_id='result with id greater than, max_id='result with id less than', include_entities='entities'"""
        query_url = self.build_query(endpoint, kwargs)
        resp, data = self.client.request(query_url)
        print(resp)

        return data

