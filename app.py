import json
import uuid
from collections import OrderedDict
from tornado import web
from utils import extract_api_params
from utils import query_data
from utils import publish_into_topic1
from utils import insert_data_to_google_spanner


class AfterShip404Handler(web.RequestHandler):
    """
    Self 404 Handler
    """
    @web.asynchronous
    def prepare(self):
        """
        Override prepare() instead of get() to cover all possible HTTP methods.
        """
        request_content, _ = extract_api_params(self.request)
        request_headers = self.request.headers
        request_id = request_headers.get('Request-Id') or str(uuid.uuid4())
        self.set_status(404)
        result = OrderedDict({
            "meta": {
                "code": 404,
                "message": "Not found"
            },
            'data': request_content
        })
        self.set_header("Content-Type", "application/json")
        self.set_header("Request-Id", request_id)
        self.write(json.dumps(result, ensure_ascii=False))
        self.finish()


class TrackingsHandler(web.RequestHandler):
    """
    AfterShip Courier API endpoint POST: /trackings was Implemented
    """
    @web.asynchronous
    def get(self):
        """
            Query data from database.(Need to do some research)
        """
        slug = self.get_arguments('slug')
        tracking_number = self.get_arguments('tracking_number')
        user_id = self.get_arguments('user_id')
        result_list = query_data(slug[0], tracking_number[0], user_id[0])
        result_json = result_list[0]
        self.write(result_json.encode())
        self.finish()


    # Aftership Courier API POST: /trackings
    @web.asynchronous
    def post(self):
        """
        AfterShip Courier API endpoint POST: /trackings was implemented.
        """
        # Init self.slug to None for 500 log

        request_content, too_large = extract_api_params(self.request)
        slug = request_content.get('slug')
        tracking_number = request_content.get('tracking_number')
        user_id = request_content.get('user_id')
        prepared_message = {
                "tracking_number": tracking_number,
                "slug": slug,
                "additional_fields": None,
                "user_id": user_id
            }
        publish_into_topic1(prepared_message)
        primary_id = str(uuid.uuid4())
        prepared_insertion = ('id', 'slug', 'tracking_number', 'user_id')
        prepared_data = [(primary_id, str(slug), str(tracking_number), str(user_id))]
        insert_data_to_google_spanner(prepared_insertion, prepared_data)
        response_body = "Process Successful"
        self.write(response_body)
        # In tornado asynchronous, when function self.finish() was called
        # it returns response to web client
        self.finish()
