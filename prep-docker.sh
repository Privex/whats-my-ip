#!/usr/bin/env bash
################################################################
#                                                              #
#            Docker configuration prep script for:             #
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

: ${DK_CONF="${DIR}/dkr/config"}
: ${DK_DATA="${DIR}/dkr/data"}

echo " [...] Auto-generating any missing ENV files + configs needed for docker-compose ..."

[[ -f ./docker-compose.yml ]] || cp -v example-docker-compose.yml docker-compose.yml
[[ -f .env ]] || cp -v .env.example .env

[[ -f "${DK_CONF}/caddy/Caddyfile" ]] || cp -v "${DK_CONF}/caddy/Caddyfile.example" "${DK_CONF}/caddy/Caddyfile"
[[ -f "${DK_CONF}/caddy/caddy.env" ]] || cp -v "${DK_CONF}/caddy/caddy.env.example" "${DK_CONF}/caddy/caddy.env"
[[ -f "${DK_CONF}/redis/redis.env" ]] || { echo "Touching file: ${DK_CONF}/redis/redis.env"; touch "${DK_CONF}/redis/redis.env"; };

echo " [+++] Finished generating configs."
