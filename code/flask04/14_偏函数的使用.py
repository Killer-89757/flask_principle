import functools

# 偏函数
"""
def func(a1,a2):
    print(a1,a2)

new_func = functools.partial(func,a1 = 123)
new_func(2)
"""

from flask import globals
def _lookup_req_object(name):
    # ctx
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError(_request_ctx_err_msg)
    # ctx.request
    # ctx.session
    return getattr(top, name)


new_func1 = functools.partial(_lookup_req_object, "request")
v = new_func1() # request

new_func2 = functools.partial(_lookup_req_object, "session")
y = new_func2() # session