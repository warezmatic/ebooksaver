import os, sys

'''
filesonic.com 222068
megaupload.com 78009
sharingmatrix.com 42846
wupload.com 34933
fileserve.com 29283
uploadbox.com 11620
bitroad.net 6773
duckload.com 4836
avaxsphere.com 4556
file2box.com 3143
saveqube.com 2581
uploadstation.com 1382
filesonic.in 1105
file2box.net 954
amazon.com 1108
'''

bad_domains = '''filesonic.com
megaupload.com
sharingmatrix.com
wupload.com
fileserve.com
uploadbox.com
bitroad.net
duckload.com
avaxsphere.com
file2box.com
saveqube.com
uploadstation.com
filesonic.in
file2box.net
amazon.com'''.split()


march_top = '''filepost.com
depositfiles.com
fp.io
ul.to
turbobit.net
unibytes.com
rapidgator.net
share4web.com
gigabase.com
wupload.com
fileserve.com
asfile.com
shareflare.net
1hostclick.com
hitfile.net
turbobit.name
fiberupload.com
share-online.biz
xlget.com
letitbit.net
rapidshare.com
vip-file.com'''.split()

have_parser = '''depositfiles.com
uploading.com
rapidshare.com
turbobit.net
filepost.com
hotfile.com
filefactory.com
easy-share.com
letitbit.net
ul.to
unibytes.com
fp.io
extabit.com
oron.com
ifile.it
crocko.com
ifolder.ru
turbobit.name
uploaded.to
shareflare.net
xlget.com
filejungle.com
gigabase.com
rapidgator.net
asfile.com'''.split()

stop_list='''
/list/
/folder/
/folders/
/users/'''

#sys.path.insert(0,'/home/books/work/booksaver/booksaver')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'booksaver.settings'
#from avaxhome.models import *

#for domain in bad_domains:
#    print domain, Link.objects.filter(domain=domain).count() #.delete()

s0 = set(march_top) - set(have_parser)
print list(s0 - set(bad_domains))
#print list( set(march_top) - set(have_parser.extend(bad_domains)))
