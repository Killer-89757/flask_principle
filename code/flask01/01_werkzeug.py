from werkzeug.serving import run_simple

def func(environ,start_response):
    print("请求来了")

if __name__ == '__main__':
    run_simple("127.0.0.1",5000,func)