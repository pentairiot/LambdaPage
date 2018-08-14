from LambdaPage import LambdaPage, S3LambdaPageCache


def hello(event):
    return 200, '{"message": "hello world"}'


def lambda_handler(event, context):
    cache = S3LambdaPageCache(bucket='lambda-page-cache-example', max_age=300)  # be sure this S3 bucket exists
    page = LambdaPage(cache=cache)
    page.add_endpoint(method='get', path='/', func=hello, enable_caching=True)
    page.handle_request(event)
