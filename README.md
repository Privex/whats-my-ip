# Privex's IP Information Tool

Our **IP Information Tool** is a small Python 3 web application written using the Flask framework, which allows a user to quickly see
their IPv4 address, their IPv6 address (if they have one), GeoIP information about each (city, country, ISP name, AS number), plus browser user agent.

You can test it out using our production My IP website: [Privex - What is my IP?](https://myip.privex.io)

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

 - **Ubuntu Bionic Server 18.04** is recommended, however other distros may work
 - **Redis** - Used for caching GeoIP data
 - A copy of **GeoIP2** City + ASN, or **GeoLite2** City + ASN (you can get GeoLite2 just by running the included `update_geoip.sh`)
 - **Python 3.7+** is strongly recommended (3.6 is the bare minimum)
 - Minimal hardware requirements, will probably run on as little as 512mb RAM and 1 core

# Installation

Quickstart (Tested on Ubuntu Bionic 18.04 - may work on other Debian-based distros):

```
sudo apt update -y

####
#
#  - Python 3.7 is strongly recommended, we cannot guarantee compatibility with older versions
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

**If this project has helped you, consider [grabbing a VPS or Dedicated Server from Privex](https://www.privex.io) - prices start at as little as US$8/mo (we take cryptocurrency!)**