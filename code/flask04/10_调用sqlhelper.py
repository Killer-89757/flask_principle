from sqlhelper import db


# db.fetchall(...)
# db.fetchone(...)

with db as c1:
    c1.execute('select 1')
    with db as c2:
        c1.execute('select 2')
    print(123)

