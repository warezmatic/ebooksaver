c = 0

for l in open('fetcher.log~~').xreadlines():
    if 'turbobit' in l:
        print l
        c+=1
        if c>10:
            break
