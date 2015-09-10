#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Meta thinking: python introspection """

################################
## Utilities

class Meta(object):
    """Utilities with meta in mind"""

    _latest_list = {}

    def get_latest_classes(self):
        return self._latest_list

    def set_latest_classes(self, classes):
        self._latest_list = classes

    def get_classes_from_module(self, module):
        """ Find classes inside a python module file """
        classes = dict([(name, cls) \
            for name, cls in module.__dict__.items() if isinstance(cls, type)])
        self.set_latest_classes(classes)
        return self.get_latest_classes()

    def get_new_classes_from_module(self, module):
        """ Skip classes not originated inside the module """
        classes = []
        for key, value in self.get_classes_from_module(module).items():
            if module.__name__ in value.__module__:
                classes.append(value)
        self.set_latest_classes(classes)
        return self.get_latest_classes()
