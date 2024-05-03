import functools
def auth(func):
    @functools.wraps(func)
    def inner(*args,**kwargs):
        return func(*args,**kwargs)
    return inner

@auth
def login():
    pass

print(login.__name__)
"""
login
"""