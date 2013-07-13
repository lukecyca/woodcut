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
        """Merely a smoke test
           This will ensure that the woodcut code is functioning, but will
           not effectively catch errors when rendering the example templates"""
        self.p.build()
