import threading
from threading import get_ident


def task():
    ident = get_ident()
    print(ident)


for i in range(20):
    t = threading.Thread(target=task)
    t.start()
