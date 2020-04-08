from urllib.parse import urljoin

URL = 'http://localhost:9200/'
ACTION = '_update'


def build_data_to_post(json_file):
    return build_wrapper(json_file)


def build_post_request(json_file,index, id):
    data_to_post = build_data_to_post(json_file)
    payload = "{index}/{action}/{id}".format(index=index, action=ACTION, id=id)
    url = urljoin(URL, payload)
    return url, data_to_post


def build_wrapper(data):
    return {
        'doc': data,
        'doc_as_upsert': True
    }


def build_id_to_elastic(json_id, unique_name):
    new_json_id = json_id.replace("\"","").replace("/", "_").replace(" ", "_")
    new_json_id = "{id}@{date_time}".format(id=new_json_id, date_time=unique_name)
    return new_json_id
