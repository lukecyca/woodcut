#!/usr/bin/python

from os import walk, remove, listdir
from os.path import join, abspath, relpath, getmtime, isfile, splitext
from datetime import datetime
from genshi.template import TemplateLoader, NewTextTemplate

from soupypage import SoupyPage
from romannumerals import int_to_roman
from article import Article



class Generator(object):
    def __init__(self, src_path='', build_path=''):
        self.src_path = abspath(src_path)
        self.build_path = abspath(build_path)
        
    def get_template_root(self):
        return join(self.src_path, 'templates')
        
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
        for root, dirs, files in walk(self.src_path):
            for f in files:
                if root.startswith(join(self.src_path, '20')) and f.endswith('.xhtml'):
                    a = Article(join(root,f),
                                relpath(join(root,f), self.src_path).replace('.xhtml','.html'))
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
        for t_file in listdir(self.src_path):
            (name, ext) = splitext(t_file)
            o_file = ''
            if ext == '.xhtml':
                o_file = "%s%s" % (name, '.html')
            elif ext in ['.newtxt', '.xml']:
                o_file = name
            else:
                continue
                
            print "Rendering %s" % o_file
            template = None
            title = None
            if ext == '.newtxt':
                with open(join(self.src_path, t_file)) as f:
                    template = NewTextTemplate(f)
            else:
                template_loader = TemplateLoader('.', auto_reload=True)
                template = template_loader.load(join(self.src_path, t_file))
                sp = SoupyPage()
                sp.open(join(self.src_path, t_file))
                title = SoupyPage.get_first(sp.get_meta('title'))
            stream = template.generate(meta={'title': title, 'articles': self.articles, 'path_to_root' : ''})
            fh = open(join(self.build_path, o_file), 'w')
            if ext == '.xhtml':
                fh.write(stream.render('xhtml', doctype='xhtml'))
            else:
                fh.write(stream.render())
            fh.close()
        
        
    def clean(self):
        # Delete all .html files
        for root, dirs, files in walk(self.src_path):
            for f in files:
                if f.endswith('.html'):
                    remove(join(root,f))
                

