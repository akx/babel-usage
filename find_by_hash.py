import re
from collections import defaultdict

from babel_usage_pickle import read_pickle

data = read_pickle()

d = defaultdict(list)
for row in data:
    if not re.search(r'(==|~=|<)', row['spec']):
        d[(row['hash'], row['spec'])].append(row)

for hash, rows in sorted(d.items(), key=lambda pair: len(pair[1]), reverse=True):
    if len(rows) > 10:
        print(hash, len(rows))
        print([row['path'] for row in rows])
