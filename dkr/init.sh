#!/usr/bin/env bash
################################################################
#                                                              #
#                Docker runner script for:                     #
#                                                              #
#               Privex IP Information Tool                     #
#            (C) 2021 Privex Inc.   GNU AGPL v3                #
#                                                              #
#      Privex Site: https://www.privex.io/                     #
#                                                              #
#      Github Repo: https://github.com/Privex/whats-my-ip      #
#                                                              #
################################################################

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:${PATH}"
export PATH="${HOME}/.local/bin:/snap/bin:${PATH}"

######
# Directory where the script is located, so we can source files regardless of where PWD is
######

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$DIR"

[[ -f .env ]] && source .env || true

# Override these defaults inside of `.env`
: ${HOST='0.0.0.0'}
: ${PORT='5252'}
: ${GU_WORKERS='4'}    # Number of Gunicorn worker processes
#EXTRA_ARGS=()

if (( $# > 0 )); then
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        echo "
Usage: docker run --rm -it privex/myip (host=${HOST}) (port=${PORT}) (workers=${GU_WORKERS}) [extra_args_for_gunicorn]

We recommend using Docker's environment flags for the run command, e.g. '--env-file ${HOME}/myip.env'
or '--env \"HOST=::\" --env GU_WORKERS=10'

"
        return 0
    fi
    i=0

    while (( $# > 0 )); do
        if (( i < 3 )) && [[ -n "$1" ]]; then
            (( i == 0 )) && HOST="$1" && echo " > Set HOST from CLI argument: $HOST"
            (( i == 1 )) && PORT="$1" && echo " > Set PORT from CLI argument: $PORT"
            (( i == 2 )) && GU_WORKERS="$1" && echo " > Set GU_WORKERS from CLI argument: $GU_WORKERS"
        fi
#        if (( i > 2 )); then
#            EXTRA_ARGS+=("$1")
#        fi
        i=$(( i + 1 ))
        shift
    done
fi

echo " > HOST: ${HOST}"
echo " > PORT: ${PORT}"
echo " > GU_WORKERS: ${GU_WORKERS}"
#echo " > EXTRA_ARGS:" "$(printf '%q ' "${EXTRA_ARGS[@]}")"

#if (( ${#EXTRA_ARGS[@]} > 0 )); then
#    pipenv run gunicorn -b "${HOST}:${PORT}" -w "$GU_WORKERS" "${EXTRA_ARGS[@]}" wsgi
#else
pipenv run gunicorn -b "${HOST}:${PORT}" -w "$GU_WORKERS" wsgi
#fi
