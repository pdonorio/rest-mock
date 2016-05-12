# -*- coding: utf-8 -*-

import rethinkdb as r

r.connect(host='rdb').repl()

q = r.db('webapp').table('datadmins')

colors = [
    '058789',  # green
    'bcb862',  # yellow
    '0f243d',  # grey
    'ff0000',  # red
]

for obj in q.filter({'type': 'welcome'}).run():
    i = obj['id']
    pos = obj['data']['Position']
    color = colors[pos]
    update = q.get_all(i).update({'data': {'Color': color}}).run()
    # print(obj, update)
    print("Updated %s with color %s" % (pos, color))
