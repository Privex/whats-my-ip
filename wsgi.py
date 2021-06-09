#!/usr/bin/env python3
"""

Copyright::
    +===================================================+
    |                 © 2021 Privex Inc.                |
    |               https://www.privex.io               |
    +===================================================+
    |                                                   |
    |        IP Address Information Tool                |
    |                                                   |
    |        Core Developer(s):                         |
    |                                                   |
    |          (+)  Chris (@someguy123) [Privex]        |
    |                                                   |
    +===================================================+

"""
from myip import settings
from myip.app import app

application = app

if __name__ == "__main__":
    application.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
