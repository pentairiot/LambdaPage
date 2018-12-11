# LambdaPage
Framework for serving static pages through AWS Lambda and API Gateway

### Installation
Install with pip:

```
pip install LambdaPage
```

### Examples

Simple examples with corresponding [Serverless](https://serverless.com/) configuration files can be found in the [examples directory](https://github.com/pentairiot/LambdaPage/tree/master/examples)

### Usage

A page is composed by one or more endpoints. Each endpoint should define a REST method, a path, and a function
that will handle the request with that method and path. Endpoints can also optionally specify a content-type for
the response payload, this defaults to `application/json` (static html pages should use `text/html;charset=utf-8`).

Each endpoint function should accept a single argument and return a tuple with `(status_code:int, response_body:str)`.
The argument will be a [Lambda-Proxy event](https://serverless.com/framework/docs/providers/aws/events/apigateway/#example-lambda-proxy-event-default)
Regardless of content-type, the response body should always be in string format.

LambdaPage also allows for caching responses. This should primarily be done for GET requests that require several seconds
to return. Currently only a `S3LambdaPageCache` is available, this can be added to a LambdaPage by instantiating it with
a `bucket` and optionally a `max_age` for cached items (defaults to 300 seconds). See the examples in the `examples` directory.

### Testing
This framework provides a nice wsgi test bed powered by falcon. Simply set up the LambdaPage and call `start_local()`.
Note this should be done under 'main' so Lambda doesn't try to execute this code:

```python
def hello(event):
    return 200, '{"message": "hello world"}'

if __name__ == '__main__':
    from LambdaPage import LambdaPage
    page = LambdaPage()
    page.add_endpoint(method='get', path='/', func=hello)
    page.start_local()
```
Then go to http://127.0.0.1:9000 in a browser.
