#!/usr/bin/python

import re
import sys
import os
import os.path
import logging
from shutil import copy
from datetime import datetime
from mako.template import Template
from mako.lookup import TemplateLookup


#: Location within source directory to cache compiled mako modules
MAKO_MODULES_DIR = '.mako_modules'


#: Paths to ignore when building
IGNORE_PATTERNS = [
    r'\.DS_Store$',
    r'\./\.hgignore$',
    r'\./\.gitignore$',
    r'\.swp$',
    r'^\./templates',
    r'^\./\.hg',
    r'^\./\.git',
    r'^\./{0}'.format(MAKO_MODULES_DIR),
]
for i in range(len(IGNORE_PATTERNS)):
    IGNORE_PATTERNS[i] = re.compile(IGNORE_PATTERNS[i])


logger = logging.getLogger(__package__)


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Project(object):
    def __init__(self, src_root, build_root, **kwargs):
        self.src_root = os.path.abspath(src_root)
        self.build_root = os.path.abspath(build_root)

        self.copy_flag = kwargs.get('copy')

        self.lookup = TemplateLookup(
            directories=[self.src_root],
            module_directory=os.path.join(self.src_root, MAKO_MODULES_DIR),
            output_encoding='utf-8',
            input_encoding='utf-8',
        )

        # Make any python modules in src_root/templates/ available for import
        sys.path.insert(0, os.path.join(self.src_root, 'templates'))

    def get_template_metadata(self, root_relative_src_path):
        """Opens a template and collects its __meta__ module-level dictionary"""

        # Skip non-templates
        if os.path.splitext(root_relative_src_path)[1] not in ['.mako']:
            return None

        metadata = {'src_path': os.path.normpath(root_relative_src_path),
                    'build_path': os.path.normpath(root_relative_src_path).replace('.mako', ''),
                    }

        template = Template(filename=root_relative_src_path,
                            output_encoding='utf-8',
                            input_encoding='utf-8')

        metadata.update(getattr(template.module, '__meta__', {}))

        return AttributeDict(metadata)

    def build_template(self, root_relative_src_path):
        """Builds a single template"""

        def relative_path(path):
            """Translates a root-relative path to a path relative to this file"""
            backout_path = os.path.relpath(
                '.', os.path.dirname(root_relative_src_path))
            return os.path.normpath(os.path.join(backout_path, path))

        # Absolute paths to source and build objects
        src_path = os.path.normpath(os.path.join(
            self.src_root, root_relative_src_path))
        build_path = os.path.normpath(os.path.join(
            self.build_root, root_relative_src_path))

        if os.path.exists(build_path):
            os.unlink(build_path)

        extension = os.path.splitext(src_path)[1]

        # Skip non-templates, and just link them to the source file
        if extension not in ['.mako']:
            if self.copy_flag:
                logger.info("Copying %s" % root_relative_src_path)
                copy(src_path, build_path)
            else:
                logger.info("Symlinking %s" % root_relative_src_path)
                os.symlink(src_path, build_path)
            return

        # Determine output filename
        build_path = build_path.replace('.mako', '')

        # Render the template to the output path
        logger.info("Rendering %s" %
                    root_relative_src_path.replace('.mako', ''))

        # Find this template's metadata
        (md,) = [t for t in self.templates
                 if t['src_path'] == os.path.normpath(root_relative_src_path)]

        with open(build_path, 'wb') as fh:
            mako_src = self.lookup.get_template(root_relative_src_path)
            fh.write(mako_src.render(
                relative_path=relative_path,
                templates=self.templates,
                articles=self.articles,
                meta=md,
            ))

    def _scan(self):
        """Collects metadata from all templates found in the source directory"""

        logger.info("Scanning templates")
        self.templates = []

        os.chdir(self.src_root)
        for path, dirs, files in os.walk('.'):
            for d in list(dirs):
                if any([ignore.search(os.path.join(path, d)) for ignore in IGNORE_PATTERNS]):
                    dirs.remove(d)

            for f in files:
                if not any([ignore.search(os.path.join(path, f)) for ignore in IGNORE_PATTERNS]):
                    md = self.get_template_metadata(os.path.join(path, f))
                    if md:
                        self.templates.append(md)

    def _link_articles(self):
        """For all templates that have date metadata, sort them and link them back/forth"""

        logger.info("Sorting templates")

        # If 'date' is present, sort by it
        def sort_by_date(template):
            if 'date' not in template:
                return datetime.strptime('1900-01-01', '%Y-%m-%d')
            else:
                return datetime.strptime(template['date'], '%Y-%m-%d')

        self.articles = [t for t in self.templates if t.get('date')]
        self.articles.sort(key=sort_by_date)

        # Link them back/forth
        previous = None
        for t in self.articles:
            if previous:
                t['previous'] = previous
                previous['next'] = t
            previous = t

    def build(self):
        """Recursively builds all Mako templates in the source directory,
           and copies/symlinks all other files"""

        self._scan()
        self._link_articles()

        if not os.path.exists(self.build_root):
            os.mkdir(self.build_root)
        os.chdir(self.src_root)
        for path, dirs, files in os.walk('.'):
            for d in list(dirs):
                if any([ignore.search(os.path.join(path, d)) for ignore in IGNORE_PATTERNS]):
                    dirs.remove(d)
                    logger.debug("Ignoring {0}".format(os.path.join(path, d)))
                elif not os.path.exists(os.path.join(self.build_root, path, d)):
                    os.mkdir(os.path.join(self.build_root, path, d))
            for f in files:
                if not any([ignore.search(os.path.join(path, f)) for ignore in IGNORE_PATTERNS]):
                    try:
                        self.build_template(os.path.join(path, f))
                    except Exception:
                        logger.exception(
                            'Exception in {0}'.format(os.path.join(path, f)))
                else:
                    logger.debug("Ignoring {0}".format(os.path.join(path, f)))

        logger.info("Build complete")

    def clean(self):
        """Delete everything in the build directory"""

        for root, dirs, files in os.walk(self.build_root, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))

        logger.info("Clean complete")
