# -*- coding: utf-8 -*-

import re


class Utils(object):

    def group_extrait(self, extrait):

        # Divide the value
        pattern = re.compile(r'^([^0-9]+)([\_0-9]+)([^\_]*)(.*)')
        m = pattern.match(extrait)
        if m:
            group = m.groups()
        else:
            group = ('Z', '_99999_')
        return group

    def get_numeric_extrait(self, group):
        # print("group", group)
        num = 0
        try:
            num = int(group[1].replace('_', ''))
            # if needed: http://stackoverflow.com/a/10219553/2114395
        except:
            # print("*** FAILED WITH", group)
            pass
        if num < 2:
            prob = 2.5
        else:
            prob = .5 - (num / 250)
        return num, prob

    def get_sort_value(self, extrait, num):

        # print("TEST1", extrait, num)
        if '_titre' in extrait:
            num += 10
            suffix = extrait.split('_')[::-1][0]
            # print("UHM", extrait, suffix)
        elif '_np' in extrait:
            num += 500
        elif '_MS' in extrait:
            num += 1000
            # print("I AM MS")
            # print("I AM np")
        else:
            num += 2000
        # print("TEST2", extrait, num)
        return num
