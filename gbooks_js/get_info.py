import urllib,urllib2
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
params = urllib.urlencode({'bibkeys': 'ISBN:061837943','jscmd':'viewapi','callback':'mycallback'})

#0071484809 - without image
request = urllib2.Request('http://books.google.com/books?bibkeys=0415446546&jscmd=viewapi&callback=gbook')
#request2 = urllib2.Request('http://books.google.com/books?bibkeys=9780415446549&jscmd=viewapi&callback=gbook')

opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
data = opener.open(request).read()
#data2 = opener.open(request2).read()
print data
#print data2
