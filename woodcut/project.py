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
    def __init__(self, src_root='', build_root=''):
        self.src_root = os.path.abspath(src_root)
        self.build_root = os.path.abspath(build_root)
    
    def build_file(self, root_relative_src_path):
        def relative_path(path):
            """Translates a root-relative path to a path relative to this file"""
            backout_path = os.path.relpath('.', os.path.dirname(root_relative_src_path))
            return os.path.normpath(os.path.join(backout_path, path))
        
        # Absolute paths to source and build objects
        src_path = os.path.normpath(os.path.join(self.src_root, root_relative_src_path))
        build_path = os.path.normpath(os.path.join(self.build_root, root_relative_src_path))
        
        extension = os.path.splitext(src_path)[1]
        
        # Skip non-templates, and just link them to the source file
        if extension not in ['.xhtml', '.newtxt', '.xml']:
            if os.path.exists(build_path):
                os.unlink(build_path)
            os.symlink(src_path, build_path)
            return
        
        # Determine output filename
        if extension == '.xhtml':
            build_path = os.path.splitext(build_path)[0] + '.html'
        else:
            build_path = os.path.splitext(build_path)[0]
        
        # Render the template to the output path
        print "Rendering %s" % os.path.basename(build_path)
        template = None
        meta = {}
        if extension == '.newtxt':
            with open(src_path) as f:
                template = NewTextTemplate(f)
        else:
            template_loader = TemplateLoader(self.src_root, auto_reload=True)
            template = template_loader.load(src_path)
            sp = SoupyPage()
            sp.open(src_path)
            meta['title'] = SoupyPage.get_first(sp.get_meta('title'))
        stream = template.generate(meta=meta, relative_path=relative_path)
        fh = open(build_path, 'w')
        if extension == '.xhtml':
            fh.write(stream.render('xhtml', doctype='xhtml'))
        else:
            fh.write(stream.render())
        fh.close()

    def build(self):
        os.chdir(self.src_root)
        for path, dirs, files in os.walk('.'):
            for d in dirs:
                if d in IGNORE_DIRECTORIES:
                    dirs.remove(d)
                elif not os.path.exists(os.path.join(self.build_root, path, d)):
                    os.mkdir(os.path.join(self.build_root, path, d))
            for f in [x for x in files if x not in IGNORE_FILES]:
                self.build_file(os.path.join(path, f))

    def clean(self):
        """Delete everything in the build directory"""
        for root, dirs, files in os.walk(self.build_root, topdown=False):
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
