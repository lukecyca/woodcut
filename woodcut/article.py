
from soupypage import SoupyPage
from typogrify.typogrify import typogrify
from genshi.template import TemplateLoader
from genshi import Markup

def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

class Article(object):
    def __init__(self, path, relative_url):
        self.template_filepath = path
        self.target_filepath = path.replace('.xhtml','.html')
        self.relative_url = relative_url
        
        # Get page metadata
        self.meta = {}
        sp = SoupyPage()
        sp.open(self.template_filepath)
        self.meta['disabled'] = get_first(sp.get_meta('disabled'))
        self.meta['date'] = get_first(sp.get_meta('date'))
        self.meta['title'] = get_first(sp.get_meta('title'))
        self.meta['description'] = get_first(sp.get_meta('description'))
        self.meta['imported_permalink'] = sp.get_meta('imported_permalink')
        self.meta['title_typogrify'] = Markup(typogrify(get_first(sp.get_meta('title'))))
        self.meta['next_article_url'] = '#'
        self.meta['prev_article_url'] = '#'
        self.meta['relative_url'] = self.relative_url
        self.meta['path_to_root'] = '../'
    
    def generate(self):
        # Render templates
        print "Rendering %s (%s)" % (self.relative_url, self.meta['title'])
        template_loader = TemplateLoader('.', auto_reload=True)
        article = template_loader.load(self.template_filepath)
        t = article.generate(meta=self.meta)
        
        # Output the HTML file
        fh = open(self.target_filepath, 'w')
        fh.write(t.render('html', doctype='html'))
        fh.close()