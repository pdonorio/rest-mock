# -*- coding: utf-8 -*-

import re
MYEXP = re.compile(r'^([A-Za-zàèéìòù]{2})[^0-9]+([0-9]+)[^0-9]*([0-9]*)')


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
            # suffix = extrait.split('_')[::-1][0]
            # print("UHM", extrait, suffix)
        elif '_np' in extrait:
            num += 500
            # print("I AM np")
        elif '_MS' in extrait:
            num += 1000
            # print("I AM MS")
        else:
            num += 2000
        # print("TEST2", extrait, num)
        return num

    def get_page(self, extrait):
        num = 0
        alphanum = 0
        extraitnum = 0
        m = MYEXP.match(extrait)
        if m:
            group = m.groups()
            # print(group)
            # exit(1)
            if group[2].strip() != '':
                print("FAILED double number")
                exit(1)
            else:
                extraitnum = int(group[1])

            num = (150 - int(group[1])) * 27
            alphas = group[0].lower()
            alphanum = 0
            # print(alphas, num)
            alphanum += ord(alphas[0]) - 90
            alphanum += (ord(alphas[1]) - 90) / 5
            num -= alphanum
        else:
            print("FAILED to match *%s*" % extrait)
            num = 1
            # exit(1)

        #######################
        # Boost the first extrait
        if extraitnum < 2:
            prob = 1 - ((30 - alphanum) / 20000)
        else:
            prob = 0.8 - ((20000 - num) / 20000)
        #######################
        print(extraitnum, num, prob)
        return 10000 - num, prob, extraitnum
