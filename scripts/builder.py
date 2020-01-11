from urllib.parse import urljoin

URL = 'http://localhost:9200/'
ACTION = '_update'
INDEX = -1


def build_data_to_post(row):
    def clean_global_value():
        global INDEX
        INDEX = -1

    clean_global_value()
    return build_wrapper(build_index_data(row))


def build_post_request(row, index_type, doc_type):
    data = build_data_to_post(row)
    payload = "{doc_type}/{action}/{index_type}".format(index_type=doc_type, action=ACTION, something=index_type)
    url = urljoin(URL, payload)
    return url, data


def build_index_data(row):
    def increment():
        global INDEX
        INDEX = INDEX + 1
        return INDEX

    return {
        "html": {
            "מספר הליך": row[increment()],
            "לפני": row[increment()],
            "העותרים": row[increment()],
            "המשיבים": row[increment()],
            "בשם העותרים": row[increment()],
            "בשם המשיבים": row[increment()],
            "פסק דין / החלטה": row[increment()]
        },
        "More_Details": {
            "פרטים כלליים": {
                "מספר הליך": row[increment()],
                "מדור": row[increment()],
                "תאריך הגשה": row[increment()],
                "סטטוס תיק": row[increment()],
                "מערער": row[increment()],
                "משיב": row[increment()],
                "אירוע אחרון": row[increment()]
            },
            "צדדים בתיק": {
                "עותר": [{
                    "שם": row[increment()],
                    "באי כוח": row[increment()]
                }],
                "משיב": [{
                    "שם": row[increment()],
                    "באי כוח": row[increment()]
                }]
            },
            "תיק דלמטה": [{
                "שם בית המשפט": row[increment()],
                "מספר תיק דלמטה": row[increment()],
                "ת.החלטה": row[increment()],
                "הרכב/שופט": row[increment()]
            }],
            "דיונים": [{
                "תאריך": row[increment()],
                "שעת דיון": row[increment()],
                "אולם": row[increment()],
                "גורם שיפוטי": row[increment()],
                "סטטוס": row[increment()]
            }],
            "אירועים": [
                {
                    "ארוע ראשי": row[increment()],
                    "ארוע משני": row[increment()],
                    "תאריך": row[increment()],
                    "יוזם": row[increment()]
                }
            ],
            "אישורי מסירה": [
                {
                    "נמען": row[increment()],
                    "תאריך חתימה": row[increment()]
                }
            ],
            "בקשות": {
                "section": {
                    "תיאור בקשה": row[increment()],
                    "תאריך": row[increment()],
                    "מגיש": row[increment()],
                    "נדחה מהמרשם": row[increment()]
                }
            }
        }
    }


def build_wrapper(data):
    return {
        'doc': data,
        'doc_as_upsert': True
    }
