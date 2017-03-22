import os

for fn in os.listdir('.'):
    if os.path.getsize(fn) == 310 and not ('.' in fn):
        os.remove(fn)
        print fn
