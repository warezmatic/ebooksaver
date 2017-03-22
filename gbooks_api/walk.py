import os, json

for fn in os.listdir('.'):
    if len(fn) == 12:
        f = open(fn)
        try:
            gb = json.loads(f.read())
            f.close()

            for i in gb['volumeInfo']['industryIdentifiers']:
                if i['type'] == u'ISBN_10':
                    print i['identifier']
        except:
            pass
