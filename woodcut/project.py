#!/usr/bin/python

import os
import os.path
from shutil import copy
from datetime import datetime
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import text_error_template, SyntaxException, CompileException, TemplateLookupException


IGNORE_FILES = ['.DS_Store', '.hgignore', '.gitignore']
IGNORE_DIRECTORIES = ['templates', '.hg', '.git', '.mako_modules']

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
        
    
    def build_file(self, root_relative_src_path):
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
        build_path = build_path.replace('.mako','')
        
        # Render the template to the output path
        print "Rendering %s" % root_relative_src_path.replace('.mako','')

        with open(build_path, 'w') as fh:
            try:
                mako_src = self.lookup.get_template(root_relative_src_path)
                fh.write(mako_src.render(relative_path=relative_path))
            except (CompileException, TemplateLookupException, SyntaxException), e:
                print '  {0.__class__.__name__}: {0}'.format(e)
        

    def build(self):
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
                    self.build_file(os.path.join(path, f))

    def clean(self):
        """Delete everything in the build directory"""
        for root, dirs, files in os.walk(self.build_root, topdown=False):
            for f in files:
                os.remove(os.path.join(root,f))
            for d in dirs:
                os.rmdir(os.path.join(root,d))
                