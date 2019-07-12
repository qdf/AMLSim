#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json


class read_act_config_data(object):
    def __init__(self):
        super(read_act_config_data, self).__init__()

        # pathname of the customer config file
        self.act_config_path = "config/"
        act_config_filename = "account_config.json"

        # Read in the JSON config file
        with open(self.act_config_path+act_config_filename) as json_file:
            self.act_config_data = json.load(json_file)


if __name__ == '__main__':

    # Create a variable to access the customer config data
    config_data = read_act_config_data()
