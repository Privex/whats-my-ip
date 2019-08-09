#!/bin/bash
################################################################
#                                                              #
#            Geolite2 database update script for:              #
#                                                              #
#               Privex IP Information Tool                     #
#            (C) 2019 Privex Inc.   GNU AGPL v3                #
#                                                              #
#      Privex Site: https://www.privex.io/                     #
#                                                              #
#      Github Repo: https://github.com/Privex/whats-my-ip      #
#                                                              #
################################################################

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
: ${GEOLITE_DIR='/usr/local/var/GeoIP'}

cd /tmp
mkdir -p "$GEOLITE_DIR"

echo "Removing any old Geolites from temp folder ..."
rm -rv GeoLite2-*
echo "Downloading new Geolite databases into /tmp/"
for i in ${k[@]}; do
    echo "Downloading Geolite $i ..."
    wget -q http://geolite.maxmind.com/download/geoip/database/GeoLite2-${i}.tar.gz
    echo "Extracting Geolite $i ..."
    tar xf GeoLite2-${i}.tar.gz
    echo "Installing Geolite $i into ${GEOLITE_DIR}/GeoLite2-${i}.mmdb ..."
    cp -v GeoLite2-${i}_*/GeoLite2-${i}.mmdb "${GEOLITE_DIR}/"
done
