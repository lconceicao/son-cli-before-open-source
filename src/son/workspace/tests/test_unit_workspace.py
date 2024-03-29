#  Copyright (c) 2015 SONATA-NFV, UBIWHERE
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
# Neither the name of the SONATA-NFV, UBIWHERE
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).

import os
import unittest
from son.workspace.workspace import Workspace
from unittest.mock import patch
from unittest import mock


class CreateWorkspaceTests(unittest.TestCase):

    def test___init__(self):
        """
        Verify variable assignments in init function
        :return:
        """
        # Create a new workspace
        ws = Workspace("workspace/root/dir",
                       ws_name="workspace_name",
                       log_level='log_level')

        # Verify its properties
        self.assertEqual(ws.ws_root, "workspace/root/dir")
        self.assertEqual(ws.ws_name, "workspace_name")
        self.assertEqual(ws.log_level, "log_level")

    @patch('os.makedirs')
    def test_create_dirs(self, m_makedirs):
        """
        Verify if the workspace directory structure
        is being well created.
        """
        # Create a new workspace
        ws = Workspace("workspace/root/dir",
                       ws_name="workspace_name",
                       log_level='log_level')

        # Assure directory structure is well created
        m_makedirs.return_value = None
        ws.create_dirs()
        for call in m_makedirs.call_args_list:
            assert '\'workspace/root/dir' in str(call)

    @patch('son.workspace.workspace.log')
    @patch('son.workspace.workspace.yaml')
    @patch('builtins.open')
    @patch('son.workspace.workspace.os.path')
    def test__create_from_descriptor__(self, m_path, m_open, m_yaml, m_log):
        """
        Perform several tests to the static function
        "__create_from_descriptor__" to ensure that
        workspaces are correctly created from a
        configuration descriptor"
        """
        # Make sure the workspace root dir and
        # config file do not exist by patching os.path
        m_path.join.return_value = None
        m_path.isdir.return_value = False
        m_path.isfile.return_value = False

        # Assure that None is returned using
        # non-existent root dir and config file
        self.assertEqual(
            Workspace.__create_from_descriptor__("/some/root/dir"),
            None
        )

        # Assure that an error message was logged
        self.assertTrue(m_log.error.called)

        # Make the root dir and config file exist
        m_path.isdir.return_value = True
        m_path.isfile.return_value = True

        # Create an invalid config descriptor for workspace
        conf_d = {
            'version': '0.01',
            'catalogue_servers': "['http://10.10.1.101:4011',"
                                 "'http://10.10.1.102:4011']",
            'descriptor_extension': 'yml',
            'schemas_local_master': '~/.son-schema',
            'schemas_remote_master': 'https://raw.githubusercontent.com/'
                                     'sonata-nfv/son-schema/master/',
            'platforms_dir': 'platforms',
            'catalogues_dir': 'catalogues',
            'configuration_dir': 'configuration'
        }

        # Feed this descriptor as a config file
        # by patching os.open and yaml.load methods
        m_open.return_value = None
        m_yaml.load.return_value = conf_d

        # Ensure it raises error when loading incomplete config descriptor
        self.assertRaises(
            KeyError,
            Workspace.__create_from_descriptor__,
            None
        )

        # Complete config descriptor
        conf_d['name'] = 'test workspace config'
        conf_d['log_level'] = 'info'

        # Ensure that a valid Workspace object is returned
        self.assertIsInstance(
            Workspace.__create_from_descriptor__(None),
            Workspace
        )

    @patch('son.workspace.workspace.os.path')
    @patch('son.workspace.workspace.yaml')
    @patch('builtins.open')
    def test_create_ws_descriptor(self, m_open, m_yaml, m_path):
        """
        Tests the function that generates the workspace
        configuration file. Verify that a workspace can be
        created using the file generated by this function.
        """
        # Create a new workspace
        ws = Workspace("workspace/root/dir",
                       ws_name="workspace_name",
                       log_level='log_level')

        # Patch file handling functions
        m_open.return_value = None
        m_open.write.return_value = None
        m_yaml.dump.return_value = None

        # Call function
        cfg_d = ws.create_ws_descriptor()

        # Assure that config file would be writen with the correct location
        configfile = os.path.join(ws.ws_root, Workspace.__descriptor_name__)
        self.assertEqual(m_open.call_args, mock.call(configfile, 'w'))

        # Make sure the workspace root dir and
        # config file exist by patching os.path
        m_path.isdir.return_value = True
        m_path.isfile.return_value = True

        # Patch yaml.load to return the previously obtained configuration
        m_yaml.load.return_value = cfg_d

        # Call function
        new_ws = Workspace.__create_from_descriptor__(ws.ws_root)

        # Assert returned workspace configuration is equal to the previous
        self.assertEqual(ws, new_ws)
