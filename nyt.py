# Import API Key
from secrets import NYT_API_KEY

# Import Modules
import requests
import json
from datetime import datetime


MAX_STALENESS = 30 ## 1 hour limit for cache
CACHE_NAME = "nyt_cache.json"
try:
    cache_file = open(CACHE_NAME, 'r')
    CACHE_DICTION = json.loads(cache_file.read())
    cache_file.close()
except:
    CACHE_DICTION = {}

def is_stale(cache_entry):
    now = datetime.now().timestamp()
    staleness = now - cache_entry['cache_timestamp']
    print('Staleness: ' + str(staleness))
    return staleness > MAX_STALENESS
    
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)
    
def request_with_cache(baseurl, params):
    uniq_ident = params_unique_combination(baseurl,params)
    
    try:
        cached_result = CACHE_DICTION[uniq_ident]
        print("Results found in Cache!")
        if is_stale(CACHE_DICTION[uniq_ident]):
            print("Results cached, but expired!")
            raise ValueError()
        return CACHE_DICTION[uniq_ident]
    except:
        if uniq_ident not in CACHE_DICTION:
            print("Results not found in Cache!")
        print("Making new request!")
        resp = requests.get(baseurl, params)
        CACHE_DICTION[uniq_ident] = resp.json()
        CACHE_DICTION[uniq_ident]['cache_timestamp'] = datetime.now().timestamp()
        cache_write = open(CACHE_NAME, 'w')
        cache_write.write(json.dumps(CACHE_DICTION))
        cache_write.close()
        return CACHE_DICTION[uniq_ident]
        
def get_stories(section):
    baseurl = 'https://api.nytimes.com/svc/topstories/v2/'
    extended_url = baseurl + section + '.json?'
    params = {'api-key': NYT_API_KEY}
    return request_with_cache(extended_url, params)
    
def get_headlines(nyt_results_dict):
    results = nyt_results_dict['results']
    headlines = []
    for r in results:
        headlines.append(r['title'])
    return headlines

    
story_list_json = get_stories('science')
headlines = get_headlines(story_list_json)
print("-----------------------------------")
for h in headlines:
    print(h)