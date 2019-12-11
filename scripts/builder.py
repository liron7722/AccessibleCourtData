from urllib.parse import urljoin

URL = 'http://localhost:9200/'
ACTION = '_update'


def build_data_to_post(title_of_something, something, row):
    return build_wrapper(build_index_data(title_of_something, something, row[A], row[B]))


def build_post_request(title_of_something, row, index_type):
    something = row[title_of_something]
    data = build_data_to_post(title_of_something, something, row)
    payload = "{index_type}/{action}/{something}".format(index_type=index_type, action=ACTION, something=something)
    url = urljoin(URL, payload)
    return url, data


def build_index_data(file_name, something, x, y):
    return {
        file_name: something,
        'A': {
            'B': x,
            'C': y
        }
    }


def build_wrapper(data):
    return {
        'doc': data,
        'doc_as_upsert': True
    }
