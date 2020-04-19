from urllib.parse import urljoin

URL = 'http://localhost:9200/'
POST_ACTION = '_update'
GET_ACTION = '_doc'


def build_get_request(index, id):
    payload = "{index}/{action}/{id}".format(index=index, action=GET_ACTION, id=id)
    url = urljoin(URL, payload)
    return url


def build_post_request(json_file, index, id):
    data_to_post = build_wrapper(json_file)
    payload = "{index}/{action}/{id}".format(index=index, action=POST_ACTION, id=id)
    url = urljoin(URL, payload)
    return url, data_to_post


def build_wrapper(data):
    return {
        'doc': data,
        'doc_as_upsert': True
    }


def build_elasticsearch_id(json_id):
    initial_id = build_an_initial_id(json_id)
    elasticsearch_id = build_first_continuous_number(initial_id)
    return elasticsearch_id


def build_an_initial_id(json_id):
    initial_id = json_id.split(" ")[1]  # Acceptance only of procedure number without court type
    initial_id = initial_id.replace("/", "-")  # Change the procedure number format from 'xxxx/xx' to 'xxxx-xx'
    return initial_id


def build_first_continuous_number(initial_id):
    first_continuous_number = 1  # Set an initial runner number to a procedure number
    elasticsearch_id = "{number_of_procedure}-{number}".format(number_of_procedure=initial_id, number=first_continuous_number)
    return elasticsearch_id


def rebuilding_id(current_id):
    # Extract a procedure number from the ID obtained in the following format from 'xxxx-xx-x' to 'xxxx-xx-'
    partial_id = current_id[:-1]
    # Extract a runner number and convert to an integer type
    current_number = int(current_id[-1:])
    # Promoting the number runner in 1 format from x to x + 1
    next_number = current_number + 1
    # Rebuilding the ID
    new_elasticsearch_id = "{partial_id}{number}".format(partial_id=partial_id, number=next_number)
    return new_elasticsearch_id
