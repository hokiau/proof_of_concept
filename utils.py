import json
from google.cloud import spanner
from google.cloud import pubsub

MAX_BYTE_PAYLOAD = 2 * 1024 * 1024  # 2M


def insert_data_to_google_spanner(insert_column_tuple, data_list, instance_id='spanner-test',
                                  database_id='database-test'):
    """
        Inserts sample data into the given database.
    """
    # Initiate Google Cloud Platform.
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    # Insert the data.
    with database.batch() as batch:
        batch.insert(
            table='table1_test',
            columns=insert_column_tuple,
            values=data_list)


def publish_into_topic1(data, project_id='aftership-team-maotai'):
    publisher = pubsub.PublisherClient()
    topic = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic='topic1-test',  # Set this to something appropriate.
    )
    message = json.dumps(data).encode()
    publisher.publish(topic, message)


def query_data(slug, tracking_number, user_id, instance_id='spanner-test', database_id='database-test'):
    """Queries sample data from the database using SQL."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)
    result_list = []
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            'SELECT result FROM table1_test WHERE user_id="{user_id}" AND slug="{slug}" AND tracking_number="{tracking_number}"'.format(
                user_id=user_id,
                slug=slug,
                tracking_number=tracking_number
            ))
        for row in results:
            result_list.append(row[0])
        return result_list


def extract_api_params(request):
    too_large = False
    try:
        body = request.body
        # if request_content length is too large, use '...' instead of it
        if len(str(body)) >= MAX_BYTE_PAYLOAD:
            body = b'...'
            too_large = True
        api_params = json.loads(body)
        if not isinstance(api_params, dict):
            raise json.decoder.JSONDecodeError
    except json.decoder.JSONDecodeError:
        api_params = body.decode('utf8')
    return api_params, too_large
