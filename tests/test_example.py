import unittest
import os.path
from woodcut.project import Project


EXAMPLE_ROOT = os.path.join(os.path.dirname(__file__), '../example')


class TestExampleSite(unittest.TestCase):
    def setUp(self):
        self.p = Project(
            os.path.join(EXAMPLE_ROOT, 'src'),
            os.path.join(EXAMPLE_ROOT, 'build')
        )

    def test_build(self):
        self.p.build()

    def test_index_template(self):
        self.p._scan()
        self.p._link_articles()
        self.p.build_template('index.html.mako')

    def test_htaccess_template(self):
        self.p._scan()
        self.p._link_articles()
        self.p.build_template('htaccess.conf.mako')

    def test_foo_template(self):
        self.p._scan()
        self.p._link_articles()
        self.p.build_template('articles/foo.html.mako')

    def test_unicode_template(self):
        self.p._scan()
        self.p._link_articles()
        self.p.build_template('articles/unicode.html.mako')
