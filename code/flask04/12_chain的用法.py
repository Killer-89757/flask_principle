import itertools
v1 = [11,22,33]
v2 = [55,66]

# 将两个列表的数据平铺开，形成一个迭代器对象itertools.chain(比起v = v1 + v2，会生成新列表更好)
v = itertools.chain(v1,v2)
for item in v:
    print(item)

"""
11
22
33
55
66
"""
