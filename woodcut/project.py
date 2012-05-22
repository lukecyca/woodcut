#!/usr/bin/python

import sys
import os
import os.path
from shutil import copy
from datetime import datetime
from mako.template import Template
from mako.lookup import TemplateLookup


IGNORE_FILES = ['.DS_Store', '.hgignore', '.gitignore']
IGNORE_DIRECTORIES = ['templates', '.hg', '.git', '.mako_modules']


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Project(object):
    def __init__(self, src_root, build_root, **kwargs):
        self.src_root = os.path.abspath(src_root)
        self.build_root = os.path.abspath(build_root)

        try:
            self.copy_flag = kwargs['copy']
        except KeyError:
            self.copy_flag = False

        self.lookup = TemplateLookup(directories=[self.src_root],
                                     module_directory=os.path.join(self.src_root, '.mako_modules'),
                                     output_encoding='utf-8',
                                     input_encoding='utf-8',
                                     )

        sys.path.insert(0, os.path.join(self.src_root, 'templates/util'))

    def get_template_metadata(self, root_relative_src_path):
        """Opens a template and collects its _meta dictionary"""

        # Skip non-templates, and just link them to the source file
        if os.path.splitext(root_relative_src_path)[1] not in ['.mako']:
            return

        metadata = {'src_path': os.path.normpath(root_relative_src_path),
                    'build_path': os.path.normpath(root_relative_src_path).replace('.mako', ''),
                    }

        template = Template(filename=root_relative_src_path,
                            output_encoding='utf-8',
                            input_encoding='utf-8')
        try:
            metadata.update(template.module._meta)
        except AttributeError:
            pass

        return AttributeDict(metadata)

    def build_template(self, root_relative_src_path):
        """Builds a single template"""

        def relative_path(path):
            """Translates a root-relative path to a path relative to this file"""
            backout_path = os.path.relpath('.', os.path.dirname(root_relative_src_path))
            return os.path.normpath(os.path.join(backout_path, path))

        # Absolute paths to source and build objects
        src_path = os.path.normpath(os.path.join(self.src_root, root_relative_src_path))
        build_path = os.path.normpath(os.path.join(self.build_root, root_relative_src_path))

        if os.path.exists(build_path):
            os.unlink(build_path)

        extension = os.path.splitext(src_path)[1]

        # Skip non-templates, and just link them to the source file
        if extension not in ['.mako']:
            if self.copy_flag:
                print "Copying %s" % root_relative_src_path
                copy(src_path, build_path)
            else:
                print "Symlinking %s" % root_relative_src_path
                os.symlink(src_path, build_path)
            return

        # Determine output filename
        build_path = build_path.replace('.mako', '')

        # Render the template to the output path
        print "Rendering %s" % root_relative_src_path.replace('.mako', '')

        # Find this template's metadata
        md = [t for t in self.templates if t['src_path'] == os.path.normpath(root_relative_src_path)][0]

        with open(build_path, 'w') as fh:
            try:
                mako_src = self.lookup.get_template(root_relative_src_path)
                fh.write(mako_src.render(relative_path=relative_path,
                                         templates=self.templates,
                                         articles=self.articles,
                                         meta=md,
                                         ))
            except (CompileException, TemplateLookupException, SyntaxException), e:
                print '  {0.__class__.__name__}: {0}'.format(e)

    def _scan(self):
        """Collects metadata from all templates found in the source directory"""

        self.templates = []

        os.chdir(self.src_root)
        for path, dirs, files in os.walk('.'):
            for d in list(dirs):
                if d in IGNORE_DIRECTORIES:
                    dirs.remove(d)
            for f in files:
                if f not in IGNORE_FILES:
                    md = self.get_template_metadata(os.path.join(path, f))
                    if md:
                        self.templates.append(md)

    def _link_articles(self):
        """For all templates that have date metadata, sort them and link them back/forth"""

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
                if d in IGNORE_DIRECTORIES:
                    dirs.remove(d)
                elif not os.path.exists(os.path.join(self.build_root, path, d)):
                    os.mkdir(os.path.join(self.build_root, path, d))
            for f in files:
                if f not in IGNORE_FILES:
                    self.build_template(os.path.join(path, f))

    def clean(self):
        """Delete everything in the build directory"""

        for root, dirs, files in os.walk(self.build_root, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))

