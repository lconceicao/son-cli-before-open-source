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

import logging
import requests
import yaml
import sys
import validators

log = logging.getLogger(__name__)


class CatalogueClient(object):

    CAT_URI_BASE = "/"
    CAT_URI_NS = "/network-services"             # List all NS
    CAT_URI_NS_ID = "/network-services/id/"      # Get a specific NS by ID
    CAT_URI_NS_NAME = "/network-services/name/"  # Get NS list by name
    CAT_URI_VNF = "/vnfs"                        # List all VNFs
    CAT_URI_VNF_ID = "/vnfs/id/"                 # Get a specific VNF by id
    CAT_URI_VNF_NAME = "/vnfs/name/"             # GET VNF list by name

    def __init__(self, base_url, auth=('', '')):
        # Assign parameters
        self._base_url = base_url
        self._auth = auth   # Just basic auth for now
        self._headers = {'Content-Type': 'application/x-yaml'}

        # Ensure parameters are valid
        assert validators.url(self._base_url),\
            "Failed to init catalogue client. Invalid URL: '{}'"\
            .format(self._base_url)

    @property
    def base_url(self):
        return self._base_url

    def alive(self):
        """
        Checks if the catalogue API server is alive and
        responding to requests
        :return: True=server OK,
                 False=server unavailable
        """
        url = self._base_url + CatalogueClient.CAT_URI_BASE
        try:
            response = requests.get(url,
                                    auth=self._auth,
                                    headers=self._headers)

        except requests.exceptions.InvalidURL:
            log.warning("Invalid URL: '{}'. Please specify "
                        "a valid address to a catalogue server".format(url))
            return False

        except requests.exceptions.ConnectionError:
            log.warning("Connection Error while contacting '{}'. "
                        "Error message: '{}'".format(url, sys.exc_info()))
            return False

        except:
            log.warning("Unexpected Error connecting to '{}'. "
                        "Error message: '{}'".format(url, sys.exc_info()[0]))
            raise

        return response.status_code == requests.codes.ok

    def get_list_all_ns(self):
        return self.__get_cat_object__(CatalogueClient.CAT_URI_NS, "")

    def get_ns(self, ns_id):
        """
        Obtains a specific network service (NS)
        :param ns_id: ID of NS in the form 'vendor.ns_name.version'
        :return: yaml object containing NS
        """
        cat_obj = self.__get_cat_object__(CatalogueClient.CAT_URI_NS_ID, ns_id)
        if not isinstance(cat_obj, str) and len(cat_obj) > 1:
            log.error("Obtained multiple network "
                      "services using the ID '{}'".format(ns_id))
            return

        log.debug("Obtained NS schema:\n{}".format(cat_obj))
        return yaml.load(cat_obj)

    def post_ns(self, nsd_data):
        """
        Publishes a NS descriptor to the catalogue server
        :param nsd_data:
        :return:
        """
        response = self.__post_cat_object__(
            CatalogueClient.CAT_URI_NS, nsd_data)

        if response and response.status_code != requests.codes.ok:
            log.error("Publishing failed. "
                      "HTTP code: {}".format(response.status_code))
            return

        return response

    def get_ns_by_name(self, ns_name):
        """
        Obtains a list of network services matching the ns_name
        :param ns_name: name of network service
        :return: (str) list of network services
        """
        return self.__get_cat_object__(
            CatalogueClient.CAT_URI_NS_NAME, ns_name)

    def get_list_all_vnf(self):
        return self.__get_cat_object__(CatalogueClient.CAT_URI_VNF, "")

    def get_vnf(self, vnf_id):
        """
        Obtains a specific VNF
        :param vnf_id: ID of VNF in the form 'vendor.ns_name.version'
        :return: yaml object containing VNF
        """
        cat_obj = self.__get_cat_object__(
            CatalogueClient.CAT_URI_VNF_ID, vnf_id)
        if not cat_obj:
            return

        if not isinstance(cat_obj, str) and len(cat_obj) > 1:
            log.error("Obtained multiple VNFs using ID '{}'".format(vnf_id))
            return

        log.debug("Obtained VNF schema:\n{}".format(cat_obj))
        return yaml.load(cat_obj)

    def post_vnf(self, vnf_data):
        """
        Publishes a VNF descriptor to the catalogue server
        :param vnf_data:
        :return:
        """
        response = self.__post_cat_object__(
            CatalogueClient.CAT_URI_VNF, vnf_data)
        if response is not None and response.status_code != requests.codes.ok:
            log.error("Publishing failed. "
                      "HTTP code: {}".format(response.status_code))
            return

        return response

    def get_vnf_by_name(self, vnf_name):
        """
        Obtains a list of VNFs matching the vnf_name
        :param vnf_name: name of network service
        :return: (str) list of VNFs
        """
        return self.__get_cat_object__(
            CatalogueClient.CAT_URI_VNF_NAME, vnf_name)

    def __get_cat_object__(self, cat_uri, obj_id):
        """
        Generic GET function.
        :param cat_uri:
        :param obj_id:
        :return:
        """
        url = self._base_url + cat_uri + obj_id
        response = requests.get(url, auth=self._auth, headers=self._headers)
        if not response.status_code == requests.codes.ok:
            return
        return response.text

    def __post_cat_object__(self, cat_uri, obj_data):
        """
        Generic POST function.
        :param cat_uri:
        :param obj_data:
        :return:
        """
        url = self._base_url + cat_uri
        log.debug("Object POST to: {}\n{}".format(url, obj_data))

        try:
            response = requests.post(url,
                                     data=obj_data,
                                     auth=self._auth,
                                     headers=self._headers)
            return response

        except requests.exceptions.ConnectionError:
            log.error("Connection error to server '{}'. VNF publishing "
                      "failed".format(CatalogueClient.CAT_URI_VNF))
            return
