#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import os


class UserAgent(object):
    '''
    @par the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,
        netscape for more user agent strings,you can find it in
        http://www.useragentstring.com/pages/useragentstring.php
    @sa http://www.useragentstring.com/pages/useragentstring.php
    '''
    user_agent_list = []
    useragent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'useragent.list')
    def __init__(self, user_agent=''):
        self._user_agent = user_agent
        with open(self.useragent_path, 'r') as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                self.user_agent_list.append(line.strip())

    def get(self):
        '''获取User-Agent
        '''
        if self._user_agent:
            return self._user_agent

        return random.choice(self.user_agent_list)
