import httplib
import StringIO
import gzip, json

HOST='books.google.com'

_headers='''GET /download/1273/ HTTP/1.1

User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-us,en;q=0.5

Accept-Encoding: gzip, deflate

Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7

DNT: 1

Connection: keep-alive

'''

def get_headers_dict(s):

    headers_dict = {}

    for l in s.split('\n'):
        if len(l) < 4:
            continue
        try:
            k,v = l.split(': ')
            headers_dict[k] = v
        except ValueError:
            pass

    return headers_dict

if __name__ == '__main__':

    headers = get_headers_dict(_headers)
    path = '/books?bibkeys=0415446546&jscmd=viewapi&callback=gbook'

    conn = httplib.HTTPConnection(HOST)
    conn.set_debuglevel(1)

    #conn.request('GET', path, headers=headers)
    #r = conn.getresponse()
    #compressed = r.read()

    #&dq=0787648515&hl=en&ei=H-yPTrb1KKWE4gTNx8y0AQ&sa=X&oi=book_result&ct=result&resnum=1&ved=0CCwQ6AEwAA
    path2 = '/books?bibkeys=0787648515&jscmd=viewapi&callback=gbook' #'/books?bibkeys=0071484809&jscmd=viewapi&callback=gbook'
    conn.request('GET', path2, headers=headers)
    r = conn.getresponse()
    compressed = r.read()
    js  = gzip.GzipFile(fileobj=StringIO.StringIO(compressed)).read()

    print json.loads(js[6:-2])
