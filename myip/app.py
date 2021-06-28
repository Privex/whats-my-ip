#!/usr/bin/env python3
"""
Main Flask file containing routes and primary business logic.

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
import inspect
from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv6Address, IPv6Network, ip_address, IPv4Address
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from myip import settings
from myip.core import GeoType, app, cf, dump_yaml, get_redis, get_ip, get_rdns, merge_frm, wants_type
from flask import Response, request, jsonify, render_template, render_template_string
from privex.helpers import DictDataClass, DictObject, K, STRBYTES, T, V, empty, empty_if, ip_is_v4, stringify
from privex.helpers.geoip import GeoIPResult, geolocate_ips
import geoip2.errors
import geoip2.models
import logging
import json

log = logging.getLogger(__name__)


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


def _class_dict(d: Union[type, object], fallback=None, no_private=True, no_protected=True, no_funcs=True):
    xdt = getattr(d, '__dict__', None)
    
    def _chk_func(f):
        if not no_funcs: return False
        return inspect.ismethod(f) or inspect.isfunction(f)
    
    if xdt is None: return fallback
    if no_protected:
        return {k: v for k, v in dict(d.__dict__).items() if not k.startswith('_') and not _chk_func(v)}
    if no_private:
        return {k: v for k, v in dict(d.__dict__).items() if not k.startswith('__') and not _chk_func(v)}
    return {k: v for k, v in dict(d.__dict__).items() if not _chk_func(v)}


def _try_dict(d: Any, fb_cast: Type[T] = str, try_class=True) -> Union[dict, T]:
    try:
        return dict(d)
    except Exception:
        if try_class:
            cld = d.__class__ if isinstance(d, object) else d
            if cld.__name__ not in dir(__builtins__):
                try:
                    return _class_dict(d)
                except Exception:
                    pass
        return fb_cast(d)


CONVERTERS = {
    bytes: stringify,
    GeoIPResult: DictObject,
    GeoData: DictObject,
    geoip2.models.ASN: lambda a: DictObject(a.raw),
    geoip2.models.City: lambda a: DictObject(a.raw),
    geoip2.models.Country: lambda a: DictObject(a.raw),
    GeoType: lambda a: a.value,
    IPv4Address: str, IPv6Address: str, IPv4Network: str, IPv6Network: str,
}


def _do_convert(d, fallback=None, fail=False):
    for k, v in CONVERTERS.items():
        if not isinstance(d, k) and not type(d) == k: continue
        try:
            log.debug(f"Found converter for {d!r} - calling converter function (key: {k!r}): {v!r} ")
            res = v(d)
            log.debug(f"Result after passing {d!r} to converter is: {res!r}")
            return res
        except Exception as e:
            log.warning(f"Exception while converting {d!r} - converter function (key: {k!r}): {v!r} - "
                        f"Exception was: {type(e)} - {e!s}")
            if fail: raise e
            continue
    return fallback


def _safe_obj(
    d: Any, fallback: K = None, fb_cast: Union[V, callable] = str, check_converter=True, do_unsafe_cast=True, **kwargs
) -> Union[K, V, DictObject, dict, str, Any]:
    """
    Convert an object of any kind - into a "safe" type, defined by ``safe_types`` and ``iter_types``. This is intended
    for preparing an object to be converted into JSON/YAML/etc., by ensuring only primitive types that are widely supported,
    will be contained in the final object that's outputted.
    
    By default, ``safe_types`` contains ``(str, int, float, bool)`` - and ``iter_types`` contains ``(dict, list, tuple, set)``.
    
    This will recursively iterate through the contents of an object, converting each value into a safe type in ``safe_types``,
    using either :attr:`.CONVERTERS` or ``unsafe_cast`` (default: :func:`._try_dict`).
    
    It won't convert iterables such as :class:`.dict` / :class:`.list` into a "safe" type, instead, they'll simply have
    their contents recursively casted into safe types.
    
    
    """
    safe_types = tuple(empty_if(kwargs.pop('safe_types', None), (str, int, float, bool), itr=True, zero=True))
    iter_types = tuple(empty_if(kwargs.pop('iter_types', None), (dict, list, tuple, set), itr=True, zero=True))
    unsafe_cast = kwargs.pop('unsafe_cast', _try_dict if do_unsafe_cast else fb_cast)
    iter_cast: Optional[Callable[[Union[list, tuple, set]], K]] = kwargs.pop('iter_cast', None)
    dict_cast: Optional[Callable[[Union[dict, DictObject]], K]] = kwargs.pop('dict_cast', DictObject)
    self_kw = {**dict(fallback=fallback, fb_cast=fb_cast, check_converter=check_converter, do_unsafe_cast=do_unsafe_cast), **kwargs}
    
    if check_converter:
        for k, v in CONVERTERS.items():
            if not isinstance(d, k) and not type(d) == k: continue
            try:
                log.debug(f"Found converter for {d!r} - calling converter function (key: {k!r}): {v!r} ")
                res = v(d)
                log.debug(f"Result after passing {d!r} to converter is: {res!r}")
                if res is not None:
                    if isinstance(res, safe_types): return res
                    d = res
                    break
                    # if not isinstance(res, safe_types):
                    #     return _safe_obj(d, **self_kw)
                    # return res
            except Exception as e:
                log.warning(f"Exception while converting {d!r} - converter function (key: {k!r}): {v!r} - "
                            f"Exception was: {type(e)} - {e!s}")
                continue
    if isinstance(d, safe_types):
        log.debug(f"Object {d!r} appears to be a safe type - returning normally. Safe types: {safe_types!r}")
        return d
    if isinstance(d, dict):
        log.debug(f"Object {d!r} appears to be a dict(-like) object - iterating over it, and recursively calling"
                  f" self (_safe_obj). Iter types: {iter_types!r}")
        cleanobj = {k: _safe_obj(v, **self_kw) for k, v in d.items()}
        return dict_cast(cleanobj) if dict_cast is not None else cleanobj
    if isinstance(d, iter_types):
        log.debug(f"Object {d!r} appears to be an iterable (list-like) object - iterating over it, and recursively calling"
                  f" self (_safe_obj). Iter types: {iter_types!r}")
        cleanobj = [_safe_obj(v, **self_kw) for v in d]
        log.debug(f"Object after recursive cleaning: {cleanobj!r}")
        if iter_cast is not None: return iter_cast(cleanobj)
        return d.__class__(cleanobj) if not isinstance(cleanobj, d.__class__) else cleanobj
    
    if do_unsafe_cast:
        log.debug(f"Passing {d!r} to unsafe_cast ({unsafe_cast!r})")
    
        return unsafe_cast(d, fb_cast=fb_cast, try_class=kwargs.pop('try_class', True))
    log.debug(f"Failed to convert {d!r} - returning fallback: {fallback}")
    return fallback


def _safe_dict(d: Union[T, Dict[str, Any], list], safe_types: tuple = None, **kwargs) -> Union[T, list, dict, DictObject]:
    safe_types = tuple(empty_if(safe_types, (str, int, float), itr=True, zero=True))
    iter_types = tuple(empty_if(kwargs.pop('iter_types', None), (dict, list, tuple, set), itr=True, zero=True))
    unsafe_cast = kwargs.get('unsafe_cast', _try_dict)
    
    def _call_self(xdx):
        return _safe_dict(xdx, safe_types=safe_types, **kwargs)
    
    def _so(xdx):
        return _safe_obj(xdx, safe_types=safe_types, iter_types=iter_types, unsafe_cast=unsafe_cast, **kwargs)
    
    if isinstance(d, dict):
        log.debug(f"(_safe_dict) Object {d!r} appears to be a dict(-like) object - iterating over it, and recursively calling"
                  f" _safe_obj.")
        safex = {k: _so(v) for k, v in d.items()}
        for k, v in safex.items():
            if isinstance(v, dict) and not isinstance(d[k], dict):
                log.debug(f"(_safe_dict) Found new dict - converting it's contents to be safe by calling self (_safe_dict). "
                          f"This new dict is (key: {k!r}): {v!r}")
                safex[k] = _call_self(v)
        
        # return DictObject({**safex, **unsafex, **objsafe})
        return DictObject(safex)
    
    if isinstance(d, iter_types):
        itr_cast = type(d)
        log.debug(f"(_safe_dict) Object {d!r} appears to be a iterable object - iterating over it, and recursively calling"
                  f" _safe_obj. iter_types: {iter_types!r}")
        return itr_cast([_so(v) for v in d])
    log.debug(f"(_safe_dict) Object {d!r} doesn't match known types. Passing it to _safe_obj then calling self (_safe_dict)"
              f"with it's result")
    res_so = _so(d)
    log.debug(f"Result from _safe_obj: {res_so} (original object: {d!r})")
    res_self = _call_self(_so(d))
    log.debug(f"Result from _safe_dict(_safe_obj(d)): {res_so} (original object: {d!r})")
    return res_self


def _safe_geo(
    d: Union[GeoIPResult, Dict[str, Any]], force_safe=False, str_network=True, trim_geoasn=True,
    trim_geocity=True, **kwargs
) -> Union[dict, DictObject]:
    if force_safe or not isinstance(d, (DictObject, dict)):
        d = _safe_dict(d, **kwargs)
    d = DictObject(d)
    if str_network and not isinstance(d.network, str):
        d.network = str(d.network)
    if trim_geoasn and 'geoasn_data' in d:
        del d['geoasn_data']
    if trim_geocity and 'geocity_data' in d:
        del d['geocity_data']
    return d


def get_geodata(ip, fail=False) -> Optional[GeoIPResult]:
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
    ip = str(ip)
    r, rkey = get_redis(), f'geoip:{ip}'
    cgdata: STRBYTES = r.get(rkey)

    if not empty(cgdata):
        return GeoIPResult(**json.loads(cgdata))
    
    try:
        gdata: List[Tuple[str, GeoIPResult]] = list(geolocate_ips(ip, throw=fail))
    except (AttributeError, ValueError) as e:
        log.warning(f"Exception while calling geolocate_ips({ip!r}) - reason: {type(e)} - {e!s}")
        emg = str(e).lower()
        if "no attribute 'country'" in emg or "no attribute 'city'" in emg or "no attribute 'as_name'" in emg:
            raise geoip2.errors.AddressNotFoundError(f"Address {ip!r} is invalid, or not found in GeoIP2 DBs "
                                                     f"(original exception was: {type(e)} - {e!s})")
        if fail: raise e
        return None
    data = None if empty(gdata, itr=True) else gdata[0][1]
    r.set(rkey, json.dumps(_safe_geo(data, True)), cf['GEOIP_CACHE_SEC'])
    
    return data


@dataclass
class GeoResult(DictDataClass):
    ip: Optional[Union[str, IPv4Address, IPv6Address]] = None
    ua: str = 'Empty User Agent'
    hostname: str = ''
    error: bool = False
    messages: list = field(default_factory=list)
    ip_valid: bool = False
    ip_type: str = None
    geo: Union[DictObject, GeoIPResult] = field(default_factory=DictObject)
    raw_data: Union[dict, DictObject] = field(default_factory=DictObject, repr=False)
    
    @property
    def ip_obj(self) -> Union[IPv4Address, IPv4Address]:
        return ip_address(self.ip)
    
    def init_ip(self, ip: str = None):
        self.ip = str(ip if not empty(ip) else self.ip)
        self.ip_type = 'ipv4' if isinstance(self.ip_obj, IPv4Address) else 'ipv6'
        self.ip_valid = True
        self.hostname = get_rdns(self.ip)
    
    def __post_init__(self):
        if not empty(self.ip):
            self.init_ip()
        self.ua = empty_if(self.ua, 'Empty User Agent')


def geo_view(ip: Union[str, IPv4Address, IPv4Address], ua: str = None, **extra) -> GeoResult:
    # data = DictObject(geo=DictObject(), hostname='', messages=[], ip_valid=False)
    # data = DictObject({**data, **extra})
    data = GeoResult(ip=None, ua=ua, **extra)
    # data.geo = DictObject()
    try:
        data.init_ip(ip)
        data.ip_valid = True
        gdata = get_geodata(ip)
        if gdata is None:
            raise geoip2.errors.AddressNotFoundError(f"GeoIPResult was empty!")
        data.geo = DictObject(_safe_geo(get_geodata(ip)))
        data.geo.error = False
    except geoip2.errors.AddressNotFoundError:
        msg = f"IP address '{ip}' not found in GeoIP database."
        log.info(msg)
        data.geo = DictObject(error=True, message=msg)
        data.error = True
        data.messages += [msg]
    except ValueError:
        log.warning(f'The IP address "{ip}" was not valid... Use header: {cf["USE_IP_HEADER"]} / Header: "{cf["IP_HEADER"]}"')
        data.messages += ['Invalid IP address detected']
        data.ip_valid = False
    return data


@app.route('/lookup', methods=['GET', 'POST'], defaults=dict(ip_addr=None, dtype=None, bformat=None))
@app.route('/lookup/', methods=['GET', 'POST'], defaults=dict(ip_addr=None, dtype=None, bformat=None))
@app.route('/lookup/<ip_addr>', methods=['GET', 'POST'], defaults=dict(dtype=None, bformat=None))
@app.route('/lookup/<ip_addr>/<dtype>', methods=['GET', 'POST'], defaults=dict(bformat=None))
@app.route('/lookup.<bformat>', methods=['GET', 'POST'], defaults=dict(ip_addr=None, dtype=None))
@app.route('/lookup.<bformat>/', methods=['GET', 'POST'], defaults=dict(ip_addr=None, dtype=None))
@app.route('/lookup.<bformat>/<ip_addr>', methods=['GET', 'POST'], defaults=dict(dtype=None))
@app.route('/lookup.<bformat>/<ip_addr>/<dtype>', methods=['GET', 'POST'], defaults=dict())
def view_lookup(ip_addr=None, dtype=None, bformat=None):
    frm = merge_frm(req=request)
    ip = frm.get('ip', frm.get('address', frm.get('addr', frm.get('ip_address', ip_addr))))
    iplist = frm.get('ips', frm.get('addresses', frm.get('addrs', frm.get('ip_addresses', []))))
    ua = request.headers.get('User-Agent', 'N/A')

    wanted = wants_type() if 'format' in frm else wants_type(fmt=bformat)

    if not empty(iplist, itr=True) and isinstance(iplist, str):
        iplist = iplist.split(',')
    
    if not empty(iplist, itr=True) and isinstance(iplist, (list, tuple)):
        if len(iplist) > settings.MAX_ADDRESSES:
            ecode, emsg = "TOO_MANY_ADDRS", f"Too many addresses. You can only lookup {settings.MAX_ADDRESSES} addresses at a time."
            if not empty(dtype) or wanted == 'text':
                return Response(f"ERROR: {emsg} (code: {ecode})", status=402, content_type='text/plain')
            edict = dict(error=True, code=ecode, message=emsg)
            if wanted == 'yaml':
                return Response(dump_yaml(edict), status=402, content_type='text/yaml')
            return jsonify(edict), 402

        if not empty(dtype) or wanted == 'text':
            dtype = empty_if(dtype, frm.get('type', frm.get('dtype', 'all')))
            _ln = "\n==========================================================\n"
            res_txt = _ln.lstrip('\n')
            for xip in iplist:
                res_txt += get_flat(xip, ua=ua, dtype=dtype) + "\n" + _ln
            return Response(res_txt, status=200, content_type='text/plain')
        res_list = {xip: geo_view(xip, ua=ua) for xip in iplist}

        rdct = {k: _safe_dict(v) for k, v in res_list.items()}
        if wanted == 'yaml':
            return Response(dump_yaml(dict(addresses=rdct)), status=200, content_type='text/yaml')
        return jsonify(rdct)

    ip = get_ip() if empty(ip) else ip
    # ua = h.get('User-Agent', 'Empty User Agent')
    
    data = dict(geo_view(ip, ua=ua))

    # wanted = wants_type()
    if not empty(dtype) or wanted == 'text':
        dtype = empty_if(dtype, frm.get('type', frm.get('dtype', 'all')))
        fres = get_flat(ip, ua=ua, dtype=dtype) + "\n"
        return Response(fres, status=200, content_type='text/plain')
    if wanted == 'yaml':
        return Response(dump_yaml(data), status=200, content_type='text/yaml')
    return jsonify(data)
    # if want_json():
    #     return jsonify(data)
    # else:
    #     return render_template('index.html', v4_host=cf['V4_HOST'], v6_host=cf['V6_HOST'], **data)


@app.route('/api')
@app.route('/api/')
@app.route('/api.html')
def view_api_docs():
    tpl = settings.TEMPLATES_DIR / 'api.md'
    md = markdown.Markdown(extensions=[TocExtension(title='Table of Contents'), FencedCodeExtension()])
    with open(tpl, 'r') as fh:
        htres = md.convert(fh.read())
    # ctx = dict(v4_host=settings.V4_HOST, v6_host=settings.V6_HOST, main_host=settings.MAIN_HOST)
    return render_template(
        'mdpage.html', content=render_template_string(htres)
    )


@app.route('/flat/', defaults=dict(dtype=None), methods=['GET', 'POST'])
@app.route('/flat', defaults=dict(dtype=None), methods=['GET', 'POST'])
@app.route('/flat/<dtype>', methods=['GET', 'POST'])
def view_flat(dtype=None):
    h = request.headers
    ip = get_ip()
    ua = h.get('User-Agent', 'N/A')
    fres = get_flat(ip, ua=ua, dtype=dtype) + "\n"
    return Response(fres, status=200, mimetype='text/plain', content_type='text/plain')


def get_flat(ip: str, ua: str = None, dtype: str = None, geodata: Union[GeoIPResult, DictObject] = None) -> str:
    # h = request.headers
    # ip = get_ip()
    # ua = h.get('User-Agent', 'N/A')
    ua = empty_if(ua, 'N/A')
    dtype = empty_if(dtype, '')
    if dtype.lower() in ['', 'none', 'ip', 'address', 'addr', 'ipaddr', 'ipaddress', 'ip_address']: return str(ip)
    if dtype.lower() in ['ua', 'agent', 'useragent', 'user-agent', 'user_agent']: return str(ua)
    data = get_geodata(ip) if empty(geodata, itr=True) else geodata
    hostname = get_rdns(ip)
    ip_type = 'ipv4' if ip_is_v4(ip) else 'ipv6'

    if dtype.lower() in ['version', 'type', 'ipv', 'ipver', 'ipversion', 'ip_version', 'ip-version']: return str(ip_type)
    if dtype.lower() in ['dns', 'rdns', 'reverse', 'reversedns', 'host', 'hostname', 'arpa', 'rev']: return str(hostname)
    if dtype.lower() in ['country', 'region']: return str(data.country)
    if dtype.lower() in ['country_code', 'region_code', 'country-code', 'region-code', 'code']: return str(data.country_code)
    if dtype.lower() in ['city', 'area']: return str(data.city)
    if dtype.lower() in ['asfull', 'fullas', 'asnfull', 'fullasn', 'ispfull', 'fullisp', 'as_full', 'full_as', 'full_asn'
                         'isp_full', 'full_isp', 'asinfo', 'asninfo', 'as_info', 'asn_info', 'isp_info', 'ispinfo']:
        return f"{data.as_name}\nAS{data.as_number}"
    if dtype.lower() in ['as', 'asn', 'asnum', 'asnumber', 'as_number', 'isp_num', 'isp_number', 'isp_asn']: return str(data.as_number)
    if dtype.lower() in ['asname', 'ispname', 'isp', 'as_name', 'isp_name']: return str(data.as_name)
    if dtype.lower() in ['post', 'postal', 'postcode', 'post_code', 'zip', 'zipcode', 'zip_code']: return str(data.postcode)
    if dtype.lower() in ['loc', 'locate', 'location', 'countrycity', 'citycountry', 'country_city', 'city_country']:
        res = ""
        if not empty(data.city): res += f"{data.city!s}, "
        if not empty(data.postcode): res += f"{data.postcode!s}, "
        if not empty(data.country): res += f"{data.country!s}"
        return res.strip(', ')
    if dtype.lower() in ['all', 'full', 'info', 'information']:
        return f"IP: {ip}\nVersion: {ip_type}\nHostname: {hostname}\nUserAgent: {ua}\nCountry: {data.country}\n" \
               f"CountryCode: {data.country_code}\nCity: {data.city}\nPostcode: {data.postcode}\nLat: {data.lat}\n" \
               f"Long: {data.long}\nASNum: {data.as_number}\nASName: {data.as_name}\nNetwork: {data.network}\n"

    if dtype.lower() in ['lat', 'latitude']: return str(data.lat)
    if dtype.lower() in ['lon', 'long', 'longitude']: return str(data.long)
    if dtype.lower() in ['latlon', 'latlong', 'latitudelongitude', 'pos', 'position', 'cord', 'coord',
                         'coords', 'coordinate', 'coordinates',  'co-ordinates']:
        return f"{data.lat:.4f}, {data.long:.4f}"

    return str(ip)


def _index(bformat=None):
    h = request.headers
    ip = get_ip()
    ua = h.get('User-Agent', 'Empty User Agent')
    q = merge_frm(req=request)
    data = DictObject(geo_view(ip, ua=ua))
    wanted = wants_type() if 'format' in q else wants_type(fmt=bformat)
    if wanted == 'json':
        return jsonify(data)
    if wanted == 'text':
        fres = get_flat(ip, ua=ua, dtype=q.get('type', q.get('dtype', 'all')))
        return Response(fres + "\n", status=200, content_type='text/plain')
    if wanted == 'yaml':
        return Response(dump_yaml(data), status=200, content_type='text/yaml')
    # return render_template('index.html', v4_host=cf['V4_HOST'], v6_host=cf['V6_HOST'], main_host=settings.MAIN_HOST, **data)
    return render_template('index.html', **data)


@app.route('/', methods=['GET', 'POST'], defaults=dict(bformat=None), strict_slashes=False)
def index_slash(bformat=None):
    return _index(bformat)


@app.route('/index', methods=['GET', 'POST'], defaults=dict(bformat=None), strict_slashes=False)
@app.route('/index.<bformat>', methods=['GET', 'POST'], defaults=dict(), strict_slashes=False)
def index_file(bformat=None):
    return _index(bformat)


@app.context_processor
def tpl_add_hosts():
    return _tpl_add_hosts()


def _tpl_add_hosts(host: str = None, v4_host: str = None, v6_host: str = None, **kwargs) -> dict:
    filter_hosts = kwargs.pop('filter_hosts', settings.FILTER_HOSTS)
    set_trusted_hosts = kwargs.pop('set_trusted_hosts', True)
    v4_sub = kwargs.pop('v4_subdomain', settings.V4_SUBDOMAIN)
    v6_sub = kwargs.pop('v6_subdomain', settings.V6_SUBDOMAIN)
    main_host = kwargs.pop('main_host', settings.MAIN_HOST)
    force_main_host = kwargs.pop('force_main_host', settings.FORCE_MAIN_HOST)
    
    if set_trusted_hosts:
        request.trusted_hosts = settings.ALLOWED_HOSTS if filter_hosts else None
    hst = request.host if empty(host) else host

    if not any([empty(v4_host), empty(v6_host)]):
        pass    # both v4 and v6_host are set, so we don't want to override them.
    elif force_main_host:
        # If force_main_host is true, then we shouldn't use the current requested host from ``hst``,
        # instead we use the pre-set V4_HOST and V6_HOST from settings (unless v4/v6_host are overridden)
        v4_host = empty_if(v4_host, settings.V4_HOST)
        v6_host = empty_if(v6_host, settings.V6_HOST)
    else:
        # If the current host is on the v4/v6 subdomain, then we need to trim the subdomain to avoid prepending a second subdomain
        if hst.startswith(f'{v4_sub}.'): hst = hst.replace(f'{v4_sub}.', '', 1)
        if hst.startswith(f'{v6_sub}.'): hst = hst.replace(f'{v6_sub}.', '', 1)
        v4_host, v6_host = empty_if(v4_host, f"{v4_sub}.{hst}"), empty_if(v6_host, f"{v6_sub}.{hst}")
    return dict(v4_host=v4_host, v6_host=v6_host, host=hst, main_host=main_host)


if __name__ == "__main__":
    app.run(
        debug=cf['DEBUG'],
        host=cf['HOST'],
        port=cf['PORT']
    )
