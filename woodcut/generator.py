#!/usr/bin/python

from os import walk, remove
from os.path import join, abspath, relpath, getmtime, isfile
from datetime import datetime
from genshi.template import TemplateLoader

from romannumerals import int_to_roman
from article import Article



class Generator(object):
    def __init__(self, root_path=''):
        self.root_path = abspath(root_path)
        
    def get_template_root(self):
        return join(self.root_path, 'templates')
        
    def get_template_mtime(self):
        """Returns the last time the templates were modified"""
        most_recent = getmtime(self.get_template_root())
        for root, dirs, files in walk(self.get_template_root()):
            for f in files:
                if f.endswith('.xhtml'):
                    most_recent = max(most_recent,getmtime(join(root,f)))
        return most_recent
        
    def load_articles(self):
        """Load all articles and metadata"""
        self.articles = []
        for root, dirs, files in walk(self.root_path):
            for f in files:
                if root.startswith(join(self.root_path, '20')) and f.endswith('.xhtml'):
                    a = Article(join(root,f),
                                relpath(join(root,f), self.root_path).replace('.xhtml','.html'))
                    if not a.meta['disabled']:
                        self.articles.append(a)
        print "Loaded %i articles" % len(self.articles)
        
        # Sort by date
        self.articles.sort(key=lambda a: a.meta['date'])

        # Create links between adjacent articles
        prev_a = None
        for a in self.articles:
            if prev_a:
                a.meta['prev_article_url'] = prev_a.relative_url
            prev_a = a
        prev_a = None
        for a in reversed(self.articles):
            if prev_a:
                a.meta['next_article_url'] = prev_a.relative_url
            prev_a = a
        
        # Create roman numberal serial numbers
        for i, a in enumerate(self.articles):
            a.meta['number'] = int_to_roman(i+1)
            
    def generate(self):
        self.load_articles()
        
        # Generate all articles
        template_mtime = self.get_template_mtime()
        for a in self.articles:
            # Generate only if the target is missing
            # or older than its sources
            if not isfile(a.target_filepath) or getmtime(a.target_filepath) < max(getmtime(a.template_filepath), template_mtime):
                a.generate()
                
        # Generate non-article pages
        pages = [join(self.root_path, 'index'),
                 join(self.root_path, 'backissues'),
                 ]
        for p in pages:
            print "Rendering %s.html" % p
            template_loader = TemplateLoader('.', auto_reload=True)
            index_template = template_loader.load('%s.xhtml' % p)
            t = index_template.generate(meta={'title': None, 'articles': self.articles, 'path_to_root' : ''})
            fh = open('%s.html' % p, 'w')
            fh.write(t.render('html', doctype='html'))
            fh.close()
        
        # Generate other things
        other_things = [join(self.root_path, 'lukecyca.rss.xml'),
                        join(self.root_path, 'test.ini.txt'),]
        for p in other_things:
            target_filename = p[:-4]
            print "Rendering %s" % target_filename
            template_loader = TemplateLoader('.', auto_reload=True)
            index_template = template_loader.load(p)
            t = index_template.generate(meta={'title': None, 'articles': self.articles, 'path_to_root' : ''})
            fh = open(target_filename, 'w')
            fh.write(t.render())
            fh.close()
            
        #print "Generating RSS"
        self.generate_rss()
        print "Generating httpd.ini"
        self.generate_httpdini()
        
    def clean(self):
        # Delete all .html files
        for root, dirs, files in walk(self.root_path):
            for f in files:
                if f.endswith('.html'):
                    remove(join(root,f))
        
        # Delete miscellaneous build targets
        remove(join(self.root_path, "lukecyca.xml"))
        remove(join(self.root_path, "httpd.ini"))
                
    def generate_httpdini(self):
        fh = open(join(self.root_path, 'httpd.ini'), 'w')
        fh.write('[ISAPI_Rewrite]\n\n')
        fh.write('RewriteRule /feed.* /lukecyca.xml [I,RP,CL]\n')
        fh.write('RewriteRule /20[[:digit:]/]+ /backissues.html [I,RP,CL]\n')
        fh.write('RewriteRule /category.* /backissues.html [I,RP,CL]\n')
        fh.write('\n')
        for a in self.articles:
            imported_permalink = a.meta['imported_permalink']
            for link in imported_permalink:
                link = link.partition('lukecyca.com')[2].rstrip('/')
                fh.write('RewriteRule %s.* /%s [I,RP,CL]\n' % (link, a.relative_url))
        fh.close()


