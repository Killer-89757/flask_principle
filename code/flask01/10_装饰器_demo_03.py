import functools
def auth1(func):
    print("auth1")
    @functools.wraps(func)
    def inner(*args,**kwargs):
        return func(*args,**kwargs)
    return inner


def auth0(func):
    print("auth0")
    @functools.wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner



@auth0
@auth1
def login():
    pass

login()
"""
auth1
auth0
"""