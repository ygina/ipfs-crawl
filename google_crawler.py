import json
import urllib.request

def make_request(start):
    return f'https://www.googleapis.com/customsearch/v1?q=ipfs+sites&cx=010619770360541910565%3Abbalnnqlte0&num=10&start={start}&key=AIzaSyBzAYoOC_g4bUShv25n1I97ZPqn-03X8kU'

def get_results():
    # Retrieves the first 250 search results for "ipfs sites" from Google
    results = []
    try:
        for i in range(25):
            start = 10 * i + 1
            request = make_request(start)
            raw_response = urllib.request.urlopen(request)
            response = json.loads(raw_response.read())
            results += [item['link'] for item in response['items']]
    except:
        pass
    return results

if __name__ == '__main__':
    results = get_results()
    fn = "google-search-results.txt"
    f_results = open(fn, 'w')
    for result in results:
        print(result)
        f_results.write(result + '\n')
    print(f"Found {len(results)} results.")
        
