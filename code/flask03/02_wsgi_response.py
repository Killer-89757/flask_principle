from werkzeug.serving import run_simple
from werkzeug.wrappers import Response

def func(environ, start_response):
    print('请求来了')
    response = Response('你好')
    return response(environ, start_response)


if __name__ == '__main__':
    run_simple('127.0.0.1', 5000, func)