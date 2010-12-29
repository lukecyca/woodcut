#!/usr/bin/python

import os
import os.path
from datetime import datetime
from genshi.template import TemplateLoader, NewTextTemplate

from soupypage import SoupyPage
from romannumerals import int_to_roman
from article import Article

IGNORE_FILES = ['.DS_Store']
IGNORE_DIRECTORIES = ['templates']

class Project(object):
    def __init__(self, src_path='', build_path=''):
        self.src_path = os.path.abspath(src_path)
        self.build_path = os.path.abspath(build_path)
    
    def generate_file(self, src, dest):
        ext = os.path.splitext(src)[1]
        
        # Skip non-templates, and just link them to the source file
        if ext not in ['.xhtml', '.newtxt', '.xml']:
            if os.path.exists(dest):
                os.unlink(dest)
            os.symlink(src, dest)
            return
        
        # Determine output filename
        if ext == '.xhtml':
            dest = os.path.splitext(dest)[0] + '.html'
        else:
            dest = os.path.splitext(dest)[0]
        
        # Render the template to the output path
        print "Rendering %s" % os.path.basename(dest)
        template = None
        title = None
        if ext == '.newtxt':
            with open(src) as f:
                template = NewTextTemplate(f)
        else:
            template_loader = TemplateLoader('.', auto_reload=True)
            template = template_loader.load(src)
            sp = SoupyPage()
            sp.open(src)
            title = SoupyPage.get_first(sp.get_meta('title'))
        stream = template.generate(meta={'title': title, 'path_to_root' : ''})
        fh = open(dest, 'w')
        if ext == '.xhtml':
            fh.write(stream.render('xhtml', doctype='xhtml'))
        else:
            fh.write(stream.render())
        fh.close()
        
        
    def generate(self):
        os.chdir(self.src_path)
        for path, dirs, files in os.walk('.'):
            for d in dirs:
                if d in IGNORE_DIRECTORIES:
                    dirs.remove(d)
                elif not os.path.exists(os.path.join(self.build_path, path, d)):
                    os.mkdir(os.path.join(self.build_path, path, d))
            for f in [x for x in files if x not in IGNORE_FILES]:
                self.generate_file(os.path.normpath(os.path.join(self.src_path, path, f)),
                                   os.path.normpath(os.path.join(self.build_path, path, f)) )
        
        


#    def get_template_root(self):
#        return os.path.join(self.src_path, 'templates')
#        
#    def get_template_mtime(self):
#        """Returns the last time the templates were modified"""
#        most_recent = os.getmtime(self.get_template_root())
#        for root, dirs, files in os.walk(self.get_template_root()):
#            for f in files:
#                if f.endswith('.xhtml'):
#                    most_recent = max(most_recent,getmtime(join(root,f)))
#        return most_recent
                           
    def clean(self):
        """Delete everything in the build directory"""
        for root, dirs, files in os.walk(self.build_path, topdown=False):
            for f in files:
                os.remove(os.path.join(root,f))
            for d in dirs:
                os.rmdir(os.path.join(root,d))
                
#    def load_articles(self):
#        """Load all articles and metadata"""
#        self.articles = []
#        for root, dirs, files in walk(self.src_path):
#            for f in files:
#                if root.startswith(join(self.src_path, '20')) and f.endswith('.xhtml'):
#                    a = Article(join(root,f),
#                                relpath(join(root,f), self.src_path).replace('.xhtml','.html'))
#                    if not a.meta['disabled']:
#                        self.articles.append(a)
#        print "Loaded %i articles" % len(self.articles)
#        
#        # Sort by date
#        self.articles.sort(key=lambda a: a.meta['date'])
#
#        # Create links between adjacent articles
#        prev_a = None
#        for a in self.articles:
#            if prev_a:
#                a.meta['prev_article_url'] = prev_a.relative_url
#            prev_a = a
#        prev_a = None
#        for a in reversed(self.articles):
#            if prev_a:
#                a.meta['next_article_url'] = prev_a.relative_url
#            prev_a = a
#        
#        # Create roman numberal serial numbers
#        for i, a in enumerate(self.articles):
#            a.meta['number'] = int_to_roman(i+1)
