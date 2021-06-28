#!/usr/bin/env python3
from myip.app import app
from myip import settings

if __name__ == '__main__':
    app.run(
        debug=settings.DEBUG,
        host=settings.HOST,
        port=settings.PORT,
    )

