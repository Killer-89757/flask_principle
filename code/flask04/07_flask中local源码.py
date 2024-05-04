try:
    # 协程
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        # 线程
        from thread import get_ident
    except ImportError:
        from _thread import get_ident
"""
__storage__ = {
    1111:{"stack":[waws] }
}
"""
class Local(object):

    def __init__(self):
        # self.__storage__ = {}
        # self.__ident_func__ = get_ident
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__() # 1111
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

class LocalStack(object):
    def __init__(self):
        self._local = Local()

    def push(self, obj):
        """Pushes a new item to the stack"""
        # self._local.stack ----  __getattr__
        # rv = None
        rv = getattr(self._local, "stack", None)
        if rv is None:
            # self._local.stack = [] -----> __setattr__ ----> Local().__storage__ = {thread_id:{'stack':[]}}
            self._local.stack = rv = []
        rv.append(obj)   # Local().__storage__ = {thread_id:{'stack':["waws"]}}
        return rv

    def pop(self):
        # getattr(self._local, "stack", None) ==》等价于 self._local.stack
        # 因为.stack,没有stack,走__getattr__,self.__storage__[self.__ident_func__()][name]，
        # 就拿到了self.__storage__[thread_id]['stack'],在取self.__storage__[thread_id]['stack'][-1]
        # or self.__storage__[thread_id]['stack'].pop()
        stack = getattr(self._local, "stack", None)
        if stack is None:
            return None
        elif len(stack) == 1:
            # release_local(self._local)
            # del __storage__[1111]
            return stack[-1]
        else:
            return stack.pop()

    @property
    def top(self):
        try:
            # 因为.stack,没有stack,走__getattr__,self.__storage__[self.__ident_func__()][name]，
            # 就拿到了self.__storage__[thread_id]['stack'],在取self.__storage__[thread_id]['stack'][-1]
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None

obj = LocalStack()
obj.push('waws')
obj.push('killer')

print(obj.top)

obj.pop()
obj.pop()