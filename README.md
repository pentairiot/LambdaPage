# LambdaPage
Framework for serving static pages through AWS Lambda and API Gateway

### Installation
Install with pip:

```
pip install LambdaPage
```

### Usage
A page is composed by one or more endpoints. Each endpoint should define a REST method, a path, and a function
that will handle the request with that method and path. Endpoints can also optionally specify a content-type for
the response payload, this defaults to `application/json` (static html pages should use `text/html;charset=utf-8`).

Each endpoint function should accept a single argument and return a tuple with `(status_code:int, response_body:str)`.
The argument will be a [Lambda-Proxy event](https://serverless.com/framework/docs/providers/aws/events/apigateway/#example-lambda-proxy-event-default)
Regardless of content-type, the response body should always be in string format.

LambdaPage also allows for caching responses. This should primarily be done for GET requests that require several seconds
to return. Currently only a `S3LambdaPageCache` is available, this can be added to a LambdaPage by instantiating it with
a `bucket` and optionally a `max_age` for cached items (defaults to 300 seconds). See the example below.

### Examples:
#### Basic example
```python
def hello(event):
    return 200, '{"message": "hello world"}'

def lambda_handler(event, context):
    from LambdaPage import LambdaPage
    page = LambdaPage()
    page.add_endpoint(method='get', path='/', func=hello)
    page.handle_request(event)
```

#### With caching
```python
def hello(event):
    return 200, '{"message": "hello world"}'

def lambda_handler(event, context):
    from LambdaPage import LambdaPage, S3LambdaPageCache
    cache = S3LambdaPageCache(bucket='lambda-page-cache-example', max_age=300)
    page = LambdaPage(cache=cache)
    page.add_endpoint(method='get', path='/', func=hello, enable_caching=True)
    page.handle_request(event)
```

### Deployment
Deploying the page to AWS can be done any way you like, we tend to use [serverless](https://serverless.com/) with the [serverless-python-requirements plugin](https://github.com/UnitedIncome/serverless-python-requirements). Here is an example config:

```yaml
service: HelloWorld

provider:
  name: aws
  stage: dev
  runtime: python3.6
  region: us-east-1

functions:
  HelloWorld:
    handler: HelloWorld.lambda_handler
    name: HelloWorld
    description: Serve the HelloWorld endpoint
    memorySize: 128
    timeout: 30
    role: arn:aws:iam::#{AWS::AccountId}:role/mobius/MobiusRole
    package:
      exclude:
        - "**"
        - "!*.py"
    events:
      - http:
          path: /
          method: get

```

Deploy by running:

```
serverless deploy
```


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
