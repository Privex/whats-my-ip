# Privex's IP Information Tool

Our **IP Information Tool** is a small Python 3 web application written using the Flask framework, which allows a user to quickly see
their IPv4 address, their IPv6 address (if they have one), GeoIP information about each (city, country, ISP name, AS number), plus browser user agent.

You can test it out using our production My IP website: [Privex - What is my IP?](https://myip.vc)

We operate our own **Whats My IP** service (using this project) on 3 domains as of June 2021:

- [myip.vc](https://myip.vc)
- [address.computer](https://address.computer)
- [myip.privex.io](https://myip.privex.io)

## Table of Contents

- [Privex's IP Information Tool](#privex-s-ip-information-tool)
    * [Features](#features)
- [License](#license)
- [Requirements](#requirements)
- [Docker](#docker)
    * [Solo Container](#solo-container)
    * [Docker Compose](#docker-compose)
- [Normal Installation](#normal-installation)
    * [Ubuntu/Debian Quickstart](#ubuntu-debian-quickstart)
    * [Webserver Example Configurations](#webserver-example-configurations)
        + [Example Caddy (v2) Caddyfile Configuration](#example-caddy--v2--caddyfile-configuration)
        + [Example Nginx Configuration](#example-nginx-configuration)
- [Keeping your GeoIP2 databases up-to-date](#keeping-your-geoip2-databases-up-to-date)
    * [Register for a Maxmind account to get an API key](#register-for-a-maxmind-account-to-get-an-api-key)
    * [Install the geoipupdate tool from Maxmind](#install-the-geoipupdate-tool-from-maxmind)
    * [Configure the tool with your API credentials](#configure-the-tool-with-your-api-credentials)
    * [Setup a weekly cron to update your GeoIP databases](#setup-a-weekly-cron-to-update-your-geoip-databases)
    * [Run geoipupdate to update your DBs now](#run-geoipupdate-to-update-your-dbs-now)
- [Contributing](#contributing)
- [Thanks for reading!](#thanks-for-reading-)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## Features

**The index HTML page supports:**

  - Shows the **IPv4 or IPv6 address that your browser directly connected from**, without
    using Javascript, to allow some functionality without JS.
  - Shows specifically your **IPv4 address** using a JS fetch query to the app's API via an IPv4-only subdomain 
  - Shows specifically your **IPv6 address** using a JS fetch query to the app's API via an IPv6-only subdomain
   
**Supports outputting IP information in a variety of formats**
    
   - **HTML** (index page)
   - **JSON**
   - **YAML** (yml)
   - **Plain Text** (greppable)
   - **Individual pieces of information** as plain text (like [icanhazip.com](https://icanhazip.com) - but more features)
   
**API**

   - `/` (`/index`) - Supports outputting in-depth IP information as HTML, JSON, YAML, and Plain Text; 
     format can be requested by either:
     - changing the URL extension (e.g. `index.txt`)
     - requesting via `Accept` header e.g. `Accept: application/yaml`
     - requesting via GET or POST e.g. `?format=json` (supports both url form encoded, and JSON body)
   - `/flat(/<info_name>)` - Outputs individual pieces of information about your IP address as plain text.
      - The root of the URI, e.g. `/flat` or `/flat/` outputs just the IPv4 or IPv6 address you're connecting from
        just like [icanhazip.com](https://icanhazip.com)
      - `<info_name>` can be set to various names of information you want to retrieve about your IP address, and
        it will output that individual piece of information in plain text, e.g. `/flat/country` may return `Sweden`,
        `/flat/city` may return `Stockholm`, `/flat/asn` may return `210083` (Privex's ASN), and so on.
        
        For a full listing of available `/flat` info endpoints, visit `/api/` on any of our My IP domains,
        [or just click here to see flat endpoint info on myip.vc](https://myip.vc/api/#flat-endpoint).
        

   - `/lookup(.y(a)?ml|.json|.txt)(/<address>)(/<info_name>)` - This endpoint is designed for looking up information
     about an IP address other than the one you're connecting from. However, if you just query `/lookup`, or
     one of it's extension variants without an address, it will return information about the address you're
     connecting from.
     
     - If you access the standard endpoint and specify an IPv4 or IPv6 address, then it will return information
       about that address in JSON format, e.g. `/lookup/185.130.47.1`
       
     - Just like `/index` - you can request different output formats from `/lookup`, either by changing
       the extension `/lookup.yml/2a07:e00::333`, requesting via `Accept` header e.g. `Accept: text/plain`,
       or requesting via GET or POST e.g. `?format=json`.
       
       The supported formats for lookup are: JSON (default), YAML/YML, and TXT (Plain Text).
       
     - As for `<info_name>` - this URL segment supports the same info names as `/flat`, and allows you to retrieve
       just **singular pieces of information** about an arbitrary IPv4 or IPv6 address. 
       
       For example, `/lookup/185.130.47.1/country` would output `Netherlands`, and `/lookup/2a07:e00::333/location`
       outputs `Stockholm, 173 11, Sweden`
     - It's possible to request information about multiple IP addresses at once, which will be returned as a dictionary
       (hash map / object) by specifying them in one of two ways:
       - The cleanest way, is to POST to `/lookup/` with a JSON body, containing the list (array) `addrs` which
         holds one or more IPv4 and/or IPv6 addresses as strings, e.g. `{"addrs": ["185.130.47.1", "2a07:e00::333"]}`
         
         You can test this easily using [HTTPie](https://httpie.io/docs):
         ```sh
         http -p hbHB POST https://myip.vc/lookup/ \
            'addrs:=["185.130.47.1", "2a07:e00::333", "185.130.46.92"]'
         ```
       - Alternatively, you can pass `addrs` as a string - comma separated addresses, via either GET, or
         standard form encoded POST.
         
         GET example: `/lookup?addrs=185.130.47.1,2a07:e00::333,185.130.46.92`
   

        
# License

This project is licensed under the **GNU AGPL v3**

For full details, please see `LICENSE.txt` and `AGPL-3.0.txt`.

Here's the important parts:

 - If you use this software (or substantial parts of it) to run a public service (including any separate user interfaces
   which use the API of your own running copy), **you must display a link to this software's source code wherever it is used**.

   Example: **This website uses the open source [Privex IP Information Tool](https://github.com/Privex/looking-glass)
   created by [Privex Inc.](https://www.privex.io)**

 - If you modify this software (or substantial portions of it) and make it available to the public in some
   form (whether it's just the source code, running it as a public service, or part of one)
    - The modified software (or portion) must remain under the GNU AGPL v3, i.e. same rules apply, public services must
      display a link back to the modified source code.
    - You must attribute us as the original authors, with a link back to the original source code
    - You must keep our copyright notice intact in the LICENSE.txt file

 - Some people interpret the GNU AGPL v3 "linking" rules to mean that you must release any application that interacts
   with our project under the GNU AGPL v3.

   To clarify our stance on those rules:

   - If you have a completely separate application which simply sends API requests to a copy of Privex Looking Glass
     that you run, you do not have to release your application under the GNU AGPL v3.
   - However, you ARE required to place a notice on your application, informing your users that your application
     uses Privex Looking Glass, with a clear link to the source code (see our example at the top)
   - If your application's source code **is inside of Privex IP Information Tool**, i.e. you've added your own Python
     views, templates etc. to a copy of this project, then your application is considered a modification of this
     software, and thus you DO have to release your source code under the GNU AGPL v3.

 - There is no warranty. We're not responsible if you, or others incur any damages from using this software.

 - If you can't / don't want to comply with these license requirements, or are unsure about how it may affect
   your particular usage of the software, please [contact us](https://www.privex.io/contact/).
   We may offer alternative licensing for parts of, or all of this software at our discretion.

# Requirements

 - **Ubuntu Bionic Server 18.04** or **Ubuntu Focal 20.04** is recommended, however other distros may work
 - **Redis** - Used for caching GeoIP data
 - A copy of **GeoIP2** City + ASN, or **GeoLite2** City + ASN (you can get GeoLite2 just by running the included `update_geoip.sh`)
 - **Python 3.7+** is strongly recommended (3.6 is the bare minimum).
   - Confirmed working perfectly on Python 3.8 and 3.9 too :)
 - Minimal hardware requirements, will probably run on as little as 512mb RAM and 1 core

# Docker

## Docker Compose

We include a `docker-compose` setup, which allows you to easily run a `myip` container, as well as a `redis` container, with
various container/image configuration easily managed from `docker-compose.yml`

To allow users to customise their `docker-compose.yml`, along with their `.env` and other configuration files related to the
Docker setup, they don't exist under the names which they'd actually be used by default, since they're excluded from Git to ensure
updates don't affect your existing configurations.

Thus, to generate a `docker-compose.yml` file, and the various other configuration files used by the compose file, you need to
either run `./prep-docker.sh` (purely generates any missing configuration files ), or `./start-docker.sh`
(generates missing config files, and then starts docker-compose).

If you're already familiar with `docker-compose`, or simply know that you need to make some changes to the config before the
containers are started, then you'll want prep-docker, which purely generates the configs:

```sh
# Generate any user config files which don't yet exist, such as docker-compose.yml and .env
./prep-docker.sh
```

Once you've customised your `docker-compose.yml` and `.env` to your needs (or decided that the defaults will be fine for you), run
start-docker:

```sh
# First, generates any user config files which don't yet exist, such as docker-compose.yml and .env
# Then, creates/starts the docker containers using `docker-compose up -d`
./start-docker.sh
```

Once you've ran `start-docker.sh` - you should be able to see the container `myip` and `myip-redis`
when you run `docker ps`:

```
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                        NAMES
d75146ddd7c0   privex/myip      "/app/init.sh"           2 minutes ago   Up 2 minutes   127.0.0.1:5252->5252/tcp     myip
2e411428f3d2   redis:latest     "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   127.0.0.2:6379->6379/tcp     myip-redis
```

Now all you need to do, is [setup a reverse proxy (webserver) such as Caddy or Nginx](#webserver-example-configurations), 
and point it at `127.0.0.1:5252` :)

**NOTE:** The default docker-compose will mount your local `/usr/share/GeoIP`
onto the container's `/usr/share/GeoIP` - so that the GeoIP databases can be updated independently from the container on the host.

This means that you need to make sure that your host's GeoIP2 databases are regularly updated.

To ensure your local host GeoIP2 databases stay up to date, follow the instructions in the
section [Keeping your GeoIP2 Databases Up-to-date](#keeping-your-geoip2-databases-up-to-date)

## Solo Container

You can run our `whats-my-ip` app on it's own using our official Docker image from DockerHub.

Due to the way Docker networking works, you'll generally need a reverse proxy in-front, which forwards
the client's IP as `X-REAL-IP` (all uppercase), or an alternative header which you can set
using the `IP_HEADER` environment variable.

For example, to run a container in the background, named `myip`, which exposes it's gunicorn server 
port on your host server at `127.0.0.1:5252`, and have it auto-delete itself when it's container is shutdown, 
you'd run the following command:

```sh
docker run --name myip --rm -p 127.0.0.1:5252:5252 -itd privex/myip 
```

To make sure it's started correctly, and to diagnose any issues if it didn't, check it's logs:

```sh
docker logs -t myip
```

Ideally, you need to do the following for the best experience with the docker container:

- Expose the port to your localhost using `-p 127.0.0.1:5252:5252`

- Make sure it has a sensible container name such as `myip` - for easily interacting with it,
  e.g. checking it's logs, restarting it, stopping it, etc.
  
- Mount `/usr/share/GeoIP` as a volume from your local host onto the container, so that you can regularly
  update the GeoIP databases. The ones that are included with the container, are likely to be quite old,
  as they'd only be updated whenever we update this project and release a new docker image.
  
  To do this, add `-v "/usr/share/GeoIP:/usr/share/GeoIP"` either directly before, or after
  the port exposure (`-p 127.0.0.1:5252:5252`) with a space between.
  
  To ensure your local host GeoIP2 databases stay up to date, follow the instructions in
  the section [Keeping your GeoIP2 Databases Up-to-date](#keeping-your-geoip2-databases-up-to-date)
  
- Create a `.env` file (see the `.env.example`), but avoid adding/uncommenting `HOST` or `PORT`,
  as they will cause problems in Docker. To use it, simply add the `--env-arg` CLI arguments
  to your `docker run` command, for example: `--env-file /home/youruser/myip/.env`

- Run a [webserver / reverse proxy on the host](#webserver-example-configurations) (actual bare server), 
  not in Docker. 
  
  If you run a webserver such as Caddy or Nginx within Docker, it generally won't be able to see the 
  client's IP address, at least not without some complicated docker network configuration + firewall rules.

- If possible, link the `myip` container to a `redis` container, and make sure that the `REDIS_HOST`
  environment variable contains the container name of the `redis` container (docker's link system
  will resolve a container name such as `redis` to the Docker LAN IP of the container).
  
  If you don't want to link a redis container, you should set the environment variable `CACHE_ADAPTER`
  to either `memory` (stores cache in memory, cache is lost when app is restarted), or `sqlite`
  (cache will be persisted in an sqlite3 database, but will be lost if the container is destroyed,
   e.g. when updated to a newer image). This will prevent many warnings being printed when you
  start the container / make the first request related to being unable to connect to the default
  Redis or Memcached server.
  
  You can permanently persist the SQLite3 databases used for caching with the `sqlite` cache adapter,
  simply by adding a volume bind between a folder on your local host, and `/root/.privex_cache` on
  the container, e.g. `-v "${HOME}/.privex_cache:/root/.privex_cache"`

Example full commands, including Redis linking:

```sh
touch .env
# Create a Redis container with persistent storage at ~/whats-my-ip/dkr/data/redis on the host
docker run --name redis --hostname redis --restart always -p 127.0.0.1:6379:6379 \ 
    -v "${HOME}/whats-my-ip/dkr/data/redis:/data" -itd redis

# Create the myip container - link it to the redis container, add an ENV var pointing it's Redis cache
# to the redis container, load the .env file at ~/whats-my-ip/.env, expose it's server port at 127.0.0.1:5252
docker run --name myip --link redis --restart always --env 'REDIS_HOST=redis'  \
    --env-file "${HOME}/whats-my-ip/.env" -p 127.0.0.1:5252:5252 -itd privex/myip 
```


# Normal Installation

## Ubuntu/Debian Quickstart

Quickstart (Tested on Ubuntu Bionic 18.04 - may work on other Debian-based distros):

```sh
sudo apt update -y

####
#
#  - Python 3.7, 3.8, 3.9, or newer is strongly recommended, we cannot guarantee compatibility with older versions
#  - Redis is used for caching GeoIP data for increased performance
#
####
sudo apt install -y git python3.7 python3.7-venv python3-pip redis-server

sudo adduser --gecos "" --disabled-login myip
sudo su - myip

###
# as user `myip`
###

# Clone the project
git clone https://github.com/Privex/whats-my-ip.git
cd whats-my-ip

#######
# Recommended: Use pipenv instead of normal pip for installing requirements into virtualenv
# (this is required if you want to use the bundled systemd myip.service file)
#######
pip3 install -U pipenv    # If you don't yet have pipenv, then use pip3 to install it globally.
pipenv install            # Creates a virtualenv and installs the requirements in Pipfile / Pipfile.lock
pipenv shell              # Activates the virtualenv

#######
# Alternative: If you can't / don't want to use Pipenv, then you can manually create a 
# Python 3.7 virtualenv and install the requirements into it.
#######
# Create and activate a virtualenv with Python 3.7
python3.7 -m venv venv
source venv/bin/activate
# Install the python packages required
pip3 install -r requirements.txt

#######
# Configure .env as required. Most importantly, you should set both V6_HOST and V4_HOST 
# to your IPv4 only + IPv6 only subdomains.
#######
cp .env.example .env
# edit .env with your favourite editor, adjust as needed
vim .env

#######
# Install/update the Geolite2 databases using `update_geoip.sh`.
# You may need to run this as root, as by default it installs into
# /usr/local/var/GeoIP2
#
# We recommend running it weekly on a cron to keep the GeoIP data
# up-to-date.
#
#######

sudo ./update_geoip.sh

###
# BELOW INSTRUCTIONS FOR DEVELOPMENT ONLY
###

# run flask dev server
# !!! Not safe for production. Use Gunicorn for production. !!!
flask run

###
# RUNNING IN PRODUCTION
###

# exit out of the myip user and become your normal account / root
exit

# install the systemd services
cd /home/myip/whats-my-ip
sudo cp *.service /etc/systemd/system/

# adjust the user/paths in the service files as needed
sudo vim /etc/systemd/system/myip.service

# once the service files are adjusted to your needs, enable and start them
sudo systemctl enable myip.service
sudo systemctl start myip.service

# IP Information Tool should now be running on 127.0.0.1:5151
# set up a reverse proxy such as nginx / apache pointed to the above host
# and it should be ready to go :)

```

## Webserver Example Configurations

### Example Caddy (v2) Caddyfile Configuration

```
myip.example.com, v4.myip.example.com, v6.myip.example.com
{
    root * /home/myip/whats-my-ip/static
    route /static/* {
        uri strip_prefix /static
        file_server
    }
    route /favicon.ico {
        file_server
    }
    reverse_proxy 127.0.0.1:5151 {
        header_up X-REAL-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {http.request.scheme}
        header_up X-Forwarded-Host {host}
    }
}
```

### Example Nginx Configuration

```
upstream myip {
    server 127.0.0.1:5151;
    keepalive 30;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /home/myip/whats-my-ip/static;

    index index.html index.htm index.nginx-debian.html;

    server_name myip.example.com v4.myip.example.com v6.myip.example.com;

    location / {
        proxy_pass http://myip;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-REAL-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        include /etc/nginx/proxy_params;
    }

    location /static {
        expires 7d;
        add_header Pragma public;
        add_header Cache-Control "public";
        alias /home/myip/whats-my-ip/static;
    }
}
```

# Keeping your GeoIP2 databases up-to-date

## Register for a Maxmind account to get an API key

Register for a Maxmind Account (it's FREE), so that you can get an API key to use with `geoipupdate`

The API key will allow you to use their `geoipupdate` tool for Linux/UNIX, which can be used with crontab
to automatically update your GeoIP2 databases every week, or however often you'd like.

You can register here for free: [https://www.maxmind.com/en/geolite2/signup](https://www.maxmind.com/en/geolite2/signup)

## Install the geoipupdate tool from Maxmind

On Ubuntu (and maybe Debian / debian-based distros), you can install `geoipupdate` from Maxmind's PPA:

```sh
sudo apt update -y
# You need software-properties-common to be able to install PPAs
sudo apt install -y software-properties-common
# Add/enable Maxmind's PPA repo
sudo add-apt-repository -y ppa:maxmind/ppa

# Update your repos to make sure you get the new package indexes from the PPA
sudo apt update -y
# Install the geoipupdate tool
sudo apt install -y geoipupdate
```

## Configure the tool with your API credentials

Open the file `/etc/GeoIP.conf` in whatever editor you prefer - `nano` is common and one of the easiest for users who aren't
the most familiar with using the CLI:

```sh
sudo nano /etc/GeoIP.conf 
```

Add your AccountID and LicenseKey from Maxmind, plus make sure `EditionIDs` contains all 3 databases as shown below - in
your `/etc/GeoIP.conf`

```sh
# The account ID and license key you got after registering with Maxmind for free.
AccountID 12345
LicenseKey aBCdeF12345

EditionIDs GeoLite2-ASN GeoLite2-City GeoLite2-Country

## The directory to store the database files. Defaults to /usr/share/GeoIP
DatabaseDirectory /usr/share/GeoIP
```

## Setup a weekly cron to update your GeoIP databases

Create a small script in your `/etc/cron.weekly` folder, to make sure that `geoipupdate` is automatically ran at least once per
week (Maxmind releases GeoLite updates every 1-2 weeks).

Simply paste the below commands into your terminal, and it will create the cron script for you, and mark it 
as an executable.

```sh
sudo tee /etc/cron.weekly/geoip <<"EOF"
#!/usr/bin/env bash
/usr/bin/geoipupdate

EOF

sudo chmod +x /etc/cron.weekly/geoip
```

## Run geoipupdate to update your DBs now

First, check if `/usr/share/GeoIP` exists:

```sh
sudo ls -lah /usr/share/GeoIP
```

If you see an error such as `No such file or directory` - then the folder doesn't exist yet,
and you should create it, to avoid issues:

```sh
sudo mkdir -pv /usr/share/GeoIP
```

Now you can run `geoipupdate` to update your databases now (`-v` means verbose, so it prints detailed logs):

```sh
sudo geoipupdate -v
```

If there were no obvious errors, then your databases should be updated :)

To confirm they're updated, you can simply use `ls` to check the dates on the files in the folder:

```sh
ls -lha /usr/share/GeoIP
```

You should see the database files starting with `GeoLite2-` - with a date showing sometime within
the past 2 weeks (14 days) on them:

```sh
total 80M
drwxr-xr-x   2 root root 4.0K Jun 29 18:03 .
drwxr-xr-x 108 root root 4.0K Jun 27 20:16 ..
-rw-r--r--   1 root root 1.4M Mar 15  2018 GeoIP.dat
-rw-------   1 root root    0 May  3  2020 .geoipupdate.lock
-rw-r--r--   1 root root 5.3M Mar 15  2018 GeoIPv6.dat
-rw-r--r--   1 root root 7.1M Jun 27 06:34 GeoLite2-ASN.mmdb
-rw-r--r--   1 root root  62M Jun 27 06:34 GeoLite2-City.mmdb
-rw-r--r--   1 root root 4.1M Jun 27 06:34 GeoLite2-Country.mmdb
```

You can ignore `GeoIP.dat` and `GeoIPv6.dat` if they're present - those are an older format of Maxmind's GeoIP
database which are sometimes installed by certain legacy Linux packages. `geoipupdate` doesn't affect those,
and Privex's `whats-my-ip` application does not use those.

If you've got this far without any issues - then congratulations! You've now got up-to-date GeoIP2 database files,
and the cron will ensure they stay up-to-date :)

# Contributing

We're very happy to accept pull requests, and work on any issues reported to us.

Here's some important information:

**Reporting Issues:**

 - For bug reports, you should include the following information:
     - Version of the project you're using - `git log -n1`
     - The Python package versions you have installed - `pip3 freeze`
     - Your python3 version - `python3 -V`
     - Your operating system and OS version (e.g. Ubuntu 18.04, Debian 7)
 - For feature requests / changes
     - Clearly explain the feature/change that you would like to be added
     - Explain why the feature/change would be useful to us, or other users of the tool
     - Be aware that features/changes that are complicated to add, or we simply find un-necessary for our use of the tool
       may not be added (but we may accept PRs)

**Pull Requests:**

 - We'll happily accept PRs that only add code comments or README changes
 - Use 4 spaces, not tabs when contributing to the code
 - You can use features from Python 3.4+ (we run Python 3.7+ for our projects)
    - Features that require a Python version that has not yet been released for the latest stable release
      of Ubuntu Server LTS (at this time, Ubuntu 18.04 Bionic) will not be accepted.
 - Clearly explain the purpose of your pull request in the title and description
     - What changes have you made?
     - Why have you made these changes?
 - Please make sure that code contributions are appropriately commented - we won't accept changes that involve
   uncommented, highly terse one-liners.

**Legal Disclaimer for Contributions**

Nobody wants to read a long document filled with legal text, so we've summed up the important parts here.

If you contribute content that you've created/own to projects that are created/owned by Privex, such as code or
documentation, then you might automatically grant us unrestricted usage of your content, regardless of the open source
license that applies to our project.

If you don't want to grant us unlimited usage of your content, you should make sure to place your content
in a separate file, making sure that the license of your content is clearly displayed at the start of the file
(e.g. code comments), or inside of it's containing folder (e.g. a file named LICENSE).

You should let us know in your pull request or issue that you've included files which are licensed
separately, so that we can make sure there's no license conflicts that might stop us being able
to accept your contribution.

If you'd rather read the whole legal text, it should be included as `privex_contribution_agreement.txt`.

# Thanks for reading!

**If this project has helped you,**
**consider [grabbing a VPS or Dedicated Server from Privex](https://www.privex.io) - prices**
**start at as little as US$8/mo (we take cryptocurrency!)**
