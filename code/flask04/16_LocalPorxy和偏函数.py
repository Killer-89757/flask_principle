import functools
class LocalProxy(object):
    def __init__(self, local):
        object.__setattr__(self, "_LocalProxy__local", local) # self.__local = local = request

    def _get_current_object(self):
        return self.__local() # self._LocalProxy__local()

    def __setitem__(self, key, value):
        # ctx.session[key] = value
        self._get_current_object()[key] = value

    def __getattr__(self, name):
        # ctx.request.method
        return getattr(self._get_current_object(), name)

def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError(_request_ctx_err_msg)
    return getattr(top, name)


session = LocalProxy(functools.partial(_lookup_req_object, "session")) # 函数()  自动传入session
session['k1'] = 123


request = LocalProxy(functools.partial(_lookup_req_object, "request")) # 函数() 自动传入request
request.method