# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2015
"""


class ValidationError(Exception):

    """ Maybe extend this later """

    def __init__(self, message):
        Exception.__init__(self, message)
