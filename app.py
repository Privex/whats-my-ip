#!/usr/bin/env python3
"""
Main Flask file containing routes and primary business logic.

Copyright::

    +===================================================+
    |                 © 2019 Privex Inc.                |
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
from ipaddress import ip_address, IPv4Address, IPv6Address
from core import app, cf, get_redis, get_geoip, GeoType
from flask import request, jsonify, render_template
from privex.helpers import empty
import geoip2.errors
import logging
import json

log = logging.getLogger('privex.myip')

def get_ip() -> str:
    """Return the user's IP from either the IP header (if USE_IP_HEADER is enabled), or remote_addr"""
    h = request.headers
    use_header, iphdr = cf['USE_IP_HEADER'], cf['IP_HEADER']

    if use_header:
        ip = h.get(iphdr, 'Unknown IP...')
        ip = ip.split(',')[0] if ',' in ip else ip
        return ip
    return request.remote_addr or 'Unknown IP...'


def want_json() -> bool:
    """Returns True if we should be returning a JSON response instead of HTML"""
    if cf['API_ONLY']: return True

    # Manual override with ?format=json
    fmt = request.values.get('format', 'html')
    if fmt.lower() == 'json':
        return True

    mime = request.accept_mimetypes
    for mt, _ in mime:
        # If a HTML mimetype is higher than JSON, then they probably don't want JSON.
        if 'html' in mt.lower(): return False
        if mt.lower() == 'application/json': return True
    # If in doubt, they don't want JSON.
    return False


class GeoData(dict):
    """
    Represents GeoIP data into an object with easy-access attributes, as well as standard dict compatibility

        >>> x = GeoData(city="Stockholm", country="Sweden", zip="12 345")
        >>> x.city
        'Stockholm'
        >>> x['country']
        'Sweden'
        >>> x.get('zip', '000000')
        '12 345'

    """

    def __init__(self, city="", country="", zip="", as_number="", as_name="", country_code="", *args, **kwargs):
        # Avoid problems with ``None`` by resetting the values back to "" if they're None/False
        city = "" if not city else city
        country = "" if not country else country
        zip = "" if not zip else zip
        as_number = "" if not as_number else as_number
        as_name = "" if not as_name else as_name
        country_code = "" if not country_code else country_code

        self.city, self.country, self.zip, self.as_number, self.as_name = city, country, zip, as_number, as_name
        self.country_code = country_code

        super(GeoData, self).__init__(
            city=city, country=country, zip=zip, as_number=as_number, as_name=as_name, country_code=country_code,
            *args, **kwargs
        )


def get_geodata(ip) -> GeoData:
    """
    Obtain GeoIP information for a given IPv4/v6 address, using Redis for caching to prevent excessive GeoIP2 querying.

    Returns a :class:`.GeoData` object which works as both a dictionary and an object with dot notation key access.

    Example usage:

        >>> gd = get_geodata('2a07:e00::666')
        {'city': 'Stockholm', 'country': 'Sweden', 'zip': '173 11', 'as_number': 210083, 'as_name': 'Privex Inc.'}
        >>> gd.city
        'Stockholm'
        >>> gd['country']
        'Sweden'
    
    """
    r, rkey = get_redis(), f'geoip:{ip}'
    gdata = r.get(rkey)

    if not empty(gdata):
        return GeoData(**json.loads(gdata))

    data = {}
    try:
        g = get_geoip(GeoType.CITY)
        citydata = g.city(ip)

        data['city'] = citydata.city.name
        data['country'] = citydata.country.name
        # 2 letter ISO code, e.g. SE for Sweden, or GB for Great Britain (the UK)
        data['country_code'] = citydata.country.iso_code
        data['zip'] = citydata.postal.code
    except geoip2.errors.AddressNotFoundError as e:
        raise e
    except Exception:
        log.exception('GeoIP error while getting city database info for IP "%s"', ip)
    
    try:
        g = get_geoip(GeoType.ASN)
        asdata = g.asn(ip)
        data['as_number'] = asdata.autonomous_system_number
        data['as_name'] = asdata.autonomous_system_organization
    except geoip2.errors.AddressNotFoundError as e:
        raise e
    except Exception:
        log.exception('GeoIP error while getting ASN database info for IP "%s"', ip)
    
    r.set(rkey, json.dumps(data), cf['GEOIP_CACHE_SEC'])
    
    return GeoData(**data)


@app.route('/')
def index():
    h = request.headers
    data = {'geo': {}}
    data['ip'] = ip = get_ip()
    data['ua'] = h.get('User-Agent', 'Empty User Agent')

    ip_valid = False
    data['error'] = False
    data['messages'] = []

    try:
        check_ip = ip_address(ip)
        data['ip_type'] = 'ipv4' if isinstance(check_ip, IPv4Address) else 'ipv6'
        ip_valid = True
        data['geo'] = get_geodata(ip)
        data['geo']['error'] = False
    except geoip2.errors.AddressNotFoundError:
        msg = f"IP address '{ip}' not found in GeoIP database."
        log.info(msg)
        data['geo'] = dict(error=True, message=msg)
        data['error'] = True
        data['messages'] += [msg]
    except ValueError:
        log.warning('The IP address "%s" was not valid... Use header: %s / Header: "%s"', ip, cf['USE_IP_HEADER'], cf['IP_HEADER'])
        data['messages'] += ['Invalid IP address detected']
    
    data['ip_valid'] = ip_valid
    if want_json():
        return jsonify(data)
    else:
        return render_template('index.html', v4_host=cf['V4_HOST'], v6_host=cf['V6_HOST'], **data)


if __name__ == "__main__":
    app.run(
        debug=cf['DEBUG'],
        host=cf['HOST'],
        port=cf['PORT']
    )
