from django.db import models
import paxutils as pu


class Book(models.Model):
    isbn = models.CharField(max_length=10,blank=1,null=1,db_index=True)
    site_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200,db_index=True)
    path = models.CharField(max_length=200)
    author = models.CharField(max_length=100,db_index=True)
    date = models.DateTimeField('date published',db_index=True)
    image = models.CharField(max_length=200,blank=1,null=1,default=None)
    body = models.TextField(null=1,blank=1)
    bookinfo = models.CharField(max_length=200,null=1,blank=1,db_index=True)
    pixhost_id = models.IntegerField(unique=False,db_index=True)

    def __unicode__(self):
        return '%s [%s]' % (self.title[:50],self.bookinfo)

    def admin_image(self):
        return '<img src="http://%s" />' % (self.image and self.image.replace('medium','medium')) #height=80 small
    admin_image.allow_tags = True

    def admin_link(self):
        return '<a href="http://avaxhome.ws/%s" target="_blank">%s</a>' % (self.path,  self.path[:30])
    admin_link.allow_tags = True

    def admin_links(self):
        s=''
        for l in self.link_set.all():
            s+='<li>%s</li>' % l.url

        return '<ol>%s</ol>' % s

    admin_links.allow_tags = True

    def admin_description(self):
        body_text = pu.stripHTML(self.body)
        description = None
        if len(body_text) > 200:
            btp = body_text.split('\n')
            i =- 1
            for p in btp:
                if p.count('|') >= 3:
                    break
                i += 1


            if i >= 0:
                description = ''

                btp = btp[i+2:]
                has_description = False
                for p in btp:
                    if len(p) > 80 and p.count('|') < 4:
                        description += pu.unescape(p.strip()) + '\n'
                        has_description = True
                    elif has_description:
                        break

                if description:
                    description = description.strip()

                    if description.startswith(u'\u201c'):
                        description = description[1:]

                    if description.endswith(u'\u201d'):
                        description = description[:-1]

                    description = description.strip()



        return description.replace('\n','<br/>')

    admin_description.allow_tags = True







class Link(models.Model):
    book = models.ForeignKey(Book)
    url = models.CharField(max_length=300)
    domain = models.CharField(max_length=50,db_index=True)
    format = models.CharField(max_length=4,blank=1,null=1,db_index=True)
    info = models.CharField(max_length=200,blank=1,null=1,db_index=True)
