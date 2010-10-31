#!/usr/bin/python

import datetime
import PyRSS2Gen

import os
import sys
import re
from os.path import join, getsize
from optparse import OptionParser

from genshi.template import TemplateLoader

import RomanNumerals
from Article import Article





def get_template_mtime():
    """Returns the last time the templates were modified"""
    most_recent = os.path.getmtime('root/templates')
    for root, dirs, files in os.walk('root/templates'):
        for f in files:
            if f.endswith('.xhtml'):
                most_recent = max(most_recent,os.path.getmtime(join(root,f)))
    return most_recent
    
    
def load_articles():
    # Load all articles and metadata
    articles = []
    for root, dirs, files in os.walk('root'):
        for f in files:
            if root.startswith('root/20') and f.endswith('.xhtml'):
                a = Article(join(root,f))
                if not a.meta['disabled']:
                    articles.append(a)
    print "Loaded %i articles" % len(articles)
    return articles 
    
    
def make():
    articles = load_articles()

    # Sort by date
    articles.sort(key=lambda a: a.meta['date'])

    # Link the articles together in both directions
    prev_a = None
    for a in articles:
        if prev_a:
            a.meta['prev_article_url'] = prev_a.relative_url
        prev_a = a
    prev_a = None
    for a in reversed(articles):
        if prev_a:
            a.meta['next_article_url'] = prev_a.relative_url
        prev_a = a
        
    # Number them
    for i, a in enumerate(articles):
        a.meta['number'] = RomanNumerals.int_to_roman(i+1)

    # Generate all articles
    template_mtime = get_template_mtime()
    for a in articles:
        # Generate only if the target is missing
        # or older than its sources
        if not os.path.isfile(a.target_filepath) or os.path.getmtime(a.target_filepath) < max(os.path.getmtime(a.template_filepath), template_mtime):
            a.generate()
            
            
    # Generate non-article pages
    pages = ['root/index','root/backissues']
    for p in pages:
        print "Rendering %s.html" % p
        template_loader = TemplateLoader('.', auto_reload=True)
        index_template = template_loader.load('%s.xhtml' % p)
        t = index_template.generate(meta={'title': None, 'articles': articles, 'path_to_root' : ''})
        fh = open('%s.html' % p, 'w')
        fh.write(t.render('html', doctype='html'))
        fh.close()
    
    print "Generating RSS"
    generate_rss(articles)
    print "Generating httpd.ini"
    make_httpdini(articles)
        
def clean():
    for root, dirs, files in os.walk('root'):
        for f in files:
            if f.endswith('.html'):
                os.remove(join(root,f))
    os.remove("root/lukecyca.xml")
    os.remove("root/httpd.ini")
                
def make_httpdini(articles):
    fh = open('root/httpd.ini', 'w')
    fh.write('[ISAPI_Rewrite]\n\n')
    fh.write('RewriteRule /feed.* /lukecyca.xml [I,RP,CL]\n')
    fh.write('RewriteRule /20[[:digit:]/]+ /backissues.html [I,RP,CL]\n')
    fh.write('RewriteRule /category.* /backissues.html [I,RP,CL]\n')
    fh.write('\n')
    for a in articles:
        imported_permalink = a.meta['imported_permalink']
        for link in imported_permalink:
            link = link.partition('lukecyca.com')[2].rstrip('/')
            fh.write('RewriteRule %s.* /%s [I,RP,CL]\n' % (link, a.relative_url))
    fh.close()

def generate_rss(articles):
    items = []
    for a in reversed(articles[-10:]):
        item = PyRSS2Gen.RSSItem(
                                title = a.meta['title'],
                                link = "http://lukecyca.com/%s" % a.relative_url,
                                description = a.meta['description'],
                                guid = PyRSS2Gen.Guid("http://lukecyca.com/%s" % a.relative_url),
                                pubDate = datetime.datetime.strptime(a.meta['date'],'%Y-%m-%d')
                                )
                                
        items.append(item)

    rss = PyRSS2Gen.RSS2(
                                title = "Luke Cyca Dot Calm",
                                link = "http://lukecyca.com",
                                description = "",
                                lastBuildDate = datetime.datetime.now(),
                                items=items)

    rss.write_xml(open("root/lukecyca.xml", "w"))
    
def main():
    parser = OptionParser()
    parser.add_option("--clean", action="store_true", dest="clean", default=False, help="Remove all .html files")
    parser.add_option("--make", action="store_true", dest="make", default=False, help="Make all .html files that need updating")
    (options, args) = parser.parse_args()
    
    if options.clean and options.make:
        parser.error("Please choose only one command")
        
    if options.clean:
        clean()
    elif options.make:
        make()

            
if __name__ == "__main__":
    main()
            
