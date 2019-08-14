#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json


class read_fi_config_data(object):
    def __init__(self):
        super(read_fi_config_data, self).__init__()

        # pathname of the customer config file
        self.fi_config_path = "config/"
        fi_config_filename = "financial_institution_config.json"

        # Read in the JSON config file
        with open(self.fi_config_path+fi_config_filename) as json_file:
            self.fi_config_data = json.load(json_file)


if __name__ == '__main__':

    # Create a variable to access the customer config data
    config_data = read_fi_config_data()
