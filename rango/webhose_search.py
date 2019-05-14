import json
import urllib.parse
import urllib.request


def read_webhose_key():
    webhose_api_key = None

    try:
        with open('search.key', 'r') as f:
            webhose_api_key = f.readline().strip()
    except:
        raise IOError('search.key not found')

    return webhose_api_key


def run_query(search_terms, size=10):
    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('Webhose key not found')

    root_url = 'https://webhose.io/filterWebContent'

    query_string = urllib.parse.quote(search_terms)

    search_url = ('{root_url}?token={key}&format=json&q={query}&language=english'
                  '&sort=relevancy&size={size}').format(
        root_url=root_url,
        key=webhose_api_key,
        query=query_string,
        size=size
    )
    print(search_url)

    results = []

    try:
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)

        for posts in json_response['posts']:
            results.append({'title': posts['title'],
                            'link': posts['url'],
                            'summary': posts['text'][:200]})

    except:
        print('Error when querying Webhose API')

    if results:
        print('success querying Webhose API')
    return results


if __name__ == '__main__':
    print('starting rango webhose script')
    read_webhose_key()
    run_query('python')
