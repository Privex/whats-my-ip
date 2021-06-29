#!/usr/bin/env bash
################################################################
#                                                              #
#            Geolite2 database update script for:              #
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

# Types of GeoLite2 databases to download
k=(ASN Country City)


################
# Override the installation directory by specifying on the CLI.
# Make sure the current user actually has permission to place files in that folder.
#
# Example:
#
#    user@host ~ $ GEOLITE_DIR='/usr/share/GeoIP' ./update_geoip.sh
#
: ${GEOLITE_DIR='/usr/share/GeoIP'}
: ${REMOTE_SRV='files.privex.io'}
: ${REMOTE_DIR='/cdn/extras/GeoIP'}

find-cmd() {
    [[ -f "/usr/bin/$1" || -f "/bin/$1" || -f "/usr/sbin/$1" || -f "/sbin/$1" || -f "/usr/local/bin/$1" ]]
}

xsudo() {
    if (( EUID == 0 )); then
        while (( $# > 0 )); do
            if [[ "$1" == "sudo" || "$1" == "sg-sudo" ]]; then
                >&2 echo -e "Attempted to run sudo with sudo!!!!"
                return 2
            fi
            [[ "$1" == "--" ]] && break
            if grep -Eq '^\-' <<< "$1"; then
                shift
            else
                break
            fi
        done
        env -- "$@"
        return $?
    else
        if find-cmd sudo; then
            sudo "$@"
            return $?
        elif find-cmd su; then
            su -c "$(printf '%q ' "$@")"
            return $?
        fi
    fi
}

#cd /tmp
echo -e "\n >>> Creating GeoIP folder if it doesn't already exist: $GEOLITE_DIR \n\n"

[[ -d "$GEOLITE_DIR" ]] || sudo mkdir -vp "$GEOLITE_DIR"

#echo "Removing any old Geolites from temp folder ..."
#rm -rv GeoLite2-*
echo -e "\n >>>> Downloading new Geolite databases into ${GEOLITE_DIR} \n"
for i in ${k[@]}; do
    echo -e "\n\n    > Downloading Geolite $i into ${GEOLITE_DIR} ... \n"
    #wget -q http://geolite.maxmind.com/download/geoip/database/GeoLite2-${i}.tar.gz
    sudo rsync -avch --progress "rsync://${REMOTE_SRV}${REMOTE_DIR}/GeoLite2-${i}.mmdb" "${GEOLITE_DIR}/"
    #echo "Extracting Geolite $i ..."
    #tar xf GeoLite2-${i}.tar.gz
    #echo "Installing Geolite $i into ${GEOLITE_DIR}/GeoLite2-${i}.mmdb ..."
    #cp -v GeoLite2-${i}_*/GeoLite2-${i}.mmdb "${GEOLITE_DIR}/"
    #cp -v GeoLite2-${i}.mmdb "${GEOLITE_DIR}/"
done

echo -e "\n\n +++++++++ FINISHED +++++++++ \n\n"

