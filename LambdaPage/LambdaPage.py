import boto3
import pytz
import json
import hashlib
from datetime import datetime
from io import BytesIO


class LambdaPage:
    def __init__(self, cache=None):
        self.endpoints = {}
        self.cache = cache

    def add_endpoint(self, method, path, func, content_type='application/json', enable_caching=False):
        if path not in self.endpoints:
            self.endpoints[path] = {}
        func.content_type = content_type
        func.enable_caching = enable_caching
        self.endpoints[path][method] = func

    def handle_request(self, event):
        method = event['httpMethod'].lower()
        path = event['path']
        if isinstance(event['body'], bytes):
            event['body'] = event['body'].decode()
        print('handling event: \n%s' % json.dumps(event))
        if path not in self.endpoints or method not in self.endpoints[path]:
            return {"statusCode": 404}
        func = self.endpoints[path][method]
        if self.cache is not None and func.enable_caching:
            resp = self.cache.retrieve(event)
        else:
            resp = None
        if resp is None:
            resp = func(event)
            if self.cache is not None and func.enable_caching:
                self.cache.store(event, resp)
        else:
            print('Cache hit')
        if isinstance(resp, (list, tuple)):
            status_code, body = resp
        else:
            status_code = 200
            body = resp
        if not isinstance(body, str):
            body = json.dumps(body)
        return {"statusCode": status_code,
                "headers": {"content-type": func.content_type},
                "body": body}

    def start_local(self):
        import falcon
        from wsgiref import simple_server
        app = falcon.API()

        class LambdaPageFalconResource(object):
            def __init__(self, request_handler):
                self.request_handler = request_handler

            @staticmethod
            def _req_to_event(req):
                return {
                    'path': req.path,
                    'resource': req.path,
                    'httpMethod': req.method.lower(),
                    'headers': req.headers,
                    'queryStringParameters': req.params,
                    'body': req.stream.read()
                }

            @staticmethod
            def _ret_to_resp(ret, resp):
                resp.data = ret['body'].encode()
                resp.status = getattr(falcon, 'HTTP_%i' % ret['statusCode'])
                resp.content_type = ret['headers']['content-type']

            def on_get(self, req, resp):
                event = self._req_to_event(req)
                ret = self.request_handler(event)
                self._ret_to_resp(ret, resp)

            def on_put(self, req, resp):
                event = self._req_to_event(req)
                ret = self.request_handler(event)
                self._ret_to_resp(ret, resp)

            def on_post(self, req, resp):
                event = self._req_to_event(req)
                ret = self.request_handler(event)
                self._ret_to_resp(ret, resp)

            def on_delete(self, req, resp):
                event = self._req_to_event(req)
                ret = self.request_handler(event)
                self._ret_to_resp(ret, resp)

        for path in self.endpoints:
            app.add_route(path, LambdaPageFalconResource(request_handler=self.handle_request))
        httpd = simple_server.make_server('127.0.0.1', 9000, app)
        httpd.serve_forever()


class LambdaPageCache:
    def __init__(self, max_age=300):
        self.max_age = max_age

    def retrieve(self, event):
        pass

    def store(self, event, resp):
        pass

    @staticmethod
    def get_key(event):
        event = {key: event[key] for key in ['path', 'httpMethod', 'queryStringParameters', 'body']}
        if 'body' in event and event['body'] is not None:
            event['body'] = event['body'].decode()
        return hashlib.md5(json.dumps(event, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def serialize_resp(resp):
        return json.dumps(resp)

    @staticmethod
    def deserialize_resp(resp):
        return json.loads(resp)


class S3LambdaPageCache(LambdaPageCache):
    def __init__(self, bucket, prefix='', max_age=300):
        super().__init__(max_age)
        self.bucket = boto3.resource('s3').Bucket(bucket)
        self.prefix = prefix

    def retrieve(self, event):
        key = self.get_key(event)
        obj = self.bucket.Object(self.prefix + key)
        buff = BytesIO()
        try:
            last_modified = obj.last_modified
            if (pytz.utc.localize(datetime.utcnow()) - last_modified).seconds > self.max_age:
                return None
            obj.download_fileobj(Fileobj=buff)
            buff.seek(0)
            return self.deserialize_resp(buff.read().decode())
        except Exception:
            return None

    def store(self, event, resp):
        key = self.get_key(event)
        buff = BytesIO(self.serialize_resp(resp).encode())
        buff.seek(0)
        self.bucket.upload_fileobj(Fileobj=buff, Key=self.prefix + key)