import os



def print_stats(path='../'):
    tcount = 0
    zcount = 0

    for fn in os.listdir(path):
        if not fn.startswith('http__'):
            continue

        fpath = path + fn
        size = os.path.getsize(fpath)

        tcount += 1
        if size == 0:
            zcount += 1

    print "total:",  tcount, "zero size:",  zcount


def remove_empty(path='../'):
    tcount = 0
    zcount = 0

    for fn in os.listdir(path):
        if not fn.startswith('http__'):
            continue

        fpath = path + fn
        size = os.path.getsize(fpath)

        tcount += 1
        if size == 0:
            zcount += 1
            os.remove(fpath)

    print "total:",  tcount, "removed:",  zcount




if __name__ == '__main__':
    remove_empty()
