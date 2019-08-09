#!/bin/bash
################################################################
#                                                              #
#              Production runner script for:                   #
#                                                              #
#               Privex IP Information Tool                     #
#            (C) 2019 Privex Inc.   GNU AGPL v3                #
#                                                              #
#      Privex Site: https://www.privex.io/                     #
#                                                              #
#      Github Repo: https://github.com/Privex/whats-my-ip      #
#                                                              #
################################################################


######
# Directory where the script is located, so we can source files regardless of where PWD is
######

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$DIR"

[[ -f .env ]] && source .env || echo "Warning: No .env file found."

# Override these defaults inside of `.env`
: ${HOST='127.0.0.1'}
: ${PORT='5151'}
: ${GU_WORKERS='4'}    # Number of Gunicorn worker processes

pipenv run gunicorn -b "${HOST}:${PORT}" -w "$GU_WORKERS" wsgi
