#  Copyright (c) 2015 SONATA-NFV
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).

from setuptools import setup, find_packages
import codecs
import os.path as path

# buildout build system 
# http://www.buildout.org/en/latest/docs/tutorial.html

# setup() documentation: 
# http://python-packaging-user-guide.readthedocs.org/en/latest/
# distributing/#setup-py

cwd = path.dirname(__file__)
longdesc = codecs.open(path.join(cwd, 'README.md'), 'r', 'utf-8').read()

name = 'son-monitor'
setup(
        name=name,
        license='Apache License, Version 2.0',
        version='0.9',
        url='https://github.com/sonata-nfv/son-cli',
        author_email='sonata-dev@sonata-nfv.eu',
        long_description=longdesc,
        package_dir={'': 'src'},
        packages=find_packages('src'),  # dependency resolution
        namespace_packages=['son', ],
        #include_package_data=True,
        #package_data= {
        #    'son': []
        #},
        install_requires=['setuptools', 'requests', 'gevent', 'paramiko',
                          'zerorpc'],
        zip_safe=False,
        entry_points={
            'console_scripts': [
                'son-monitor=son.monitor.monitor:main'
            ],
        }
        #test_suite='son',
        #setup_requires=['pytest-runner'],
        #tests_require=['pytest']
#test_suite='son.workspace.tests.TestSample.main'
    )
