from LambdaPage import LambdaPage


def hello(event):
    return 200, '{"message": "hello world"}'


def lambda_handler(event, context):
    page = LambdaPage()
    page.add_endpoint(method='get', path='/', func=hello)
    page.handle_request(event)
