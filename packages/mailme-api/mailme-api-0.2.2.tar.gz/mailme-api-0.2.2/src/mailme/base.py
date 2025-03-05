#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Mailme API
# Copyright (c) 2008-2024 Hive Solutions Lda.
#
# This file is part of Hive Mailme API.
#
# Hive Mailme API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Mailme API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Mailme API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

BASE_URL = "https://mailme.bemisc.com/api/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """


class API(appier.API):
    """
    Implementation of the Mailme API specification
    for a simplified python client usage.
    """

    def __init__(self, *args, **kwargs):
        appier.API.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("MAILME_BASE_URL", BASE_URL)
        self.key = appier.conf("MAILME_KEY", None)
        self.base_url = kwargs.get("base_url", self.base_url)
        self.key = appier.conf("key", self.key)

    def build(
        self,
        method,
        url,
        data=None,
        data_j=None,
        data_m=None,
        headers=None,
        params=None,
        mime=None,
        kwargs=None,
    ):
        auth = kwargs.pop("auth", True)
        if auth and self.key:
            headers["X-Secret-Key"] = self.key

    def ping(self):
        url = self.base_url + "ping"
        contents = self.get(url, auth=False)
        return contents

    def send(self, payload):
        url = self.base_url + "send"
        contents = self.post(url, data_j=payload)
        return contents


class Ping(dict):
    pass


class Attachment(dict):
    pass


class AttachmentPayload(dict):
    pass


class Message(dict):
    pass


class MessagePayload(dict):
    pass
