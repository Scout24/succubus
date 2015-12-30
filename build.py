from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.integrationtest")


name = "succubus"
summary = "Lightweight Python module for daemonizing"
default_task = "publish"
version = '1.0'
authors = [Author('Stefan Neben', "stefan.neben@immobilienscout24.de"),
           Author('Stefan Nordhausen', "stefan.nordhausen@immobilienscout24.de"),
          ]
url = 'https://github.com/ImmobilienScout24/succubus'
description = open("README.rst").read()
license = 'Apache License 2.0'


@init
def set_properties(project):
    pass

@init
def set_properties(project):
    project.set_property('install_dependencies_upgrade', True)
    project.build_depends_on("unittest2")

    # TODO: Write more tests
    project.set_property('coverage_break_build', False)


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s-%s' % (project.version, os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url', os.environ.get('PYPIPROXY_URL'))
    project.get_property('distutils_commands').append('bdist_rpm')
