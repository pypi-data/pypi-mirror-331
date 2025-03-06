# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

import glob
import os

from subprocess import check_call

import shutil

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


HERE = os.path.abspath(os.path.dirname(__file__))


def update_submodules():
    """You may run 
    
    git config --global submodule.recurse true
    """
    check_call(
        ['git', 'submodule', 'update', '--init', '--recursive'],
        cwd=HERE,
    )


def build_javascript():
    check_call(
        ['yarn', 'install'],
        cwd=HERE,
    )
    check_call(
        ['yarn', 'build:webpack', '--mode=production'],
        cwd=HERE,
    )
    for file in glob.glob(r'./dist/*.js'):
        shutil.copy(
            file,
            './datalayer_ui/static/'
        )


class JupyterBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
#        update_submodules()
        if self.target_name == 'editable':
            build_javascript()
        elif self.target_name == 'wheel':
            build_javascript()
        elif self.target_name == 'sdist':
            build_javascript()
