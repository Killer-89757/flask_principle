import time
import threading

"""
class Foo(object):
    def __init__(self):
        self.num = 0

val2 = Foo()

def task(i):
    val2.num = i
    time.sleep(1)
    print(val2.num)

for i in range(4):
    t = threading.Thread(target=task,args=(i,))
    t.start()
"""


val1 = threading.local()

def task(i):
    val1.num = i
    time.sleep(1)
    print(val1.num)

for i in range(4):
    t = threading.Thread(target=task,args=(i,))
    t.start()
