Programmatic usage of our IP Information service
================================================

[TOC]

## Supported output formats

Some of our pages / endpoints support outputting their data in multiple formats.

You can select a format either by using `?format=TYPE` - which is high priority, or you can use the `Accept:` header.

You can also specify `format` as both an encoded POST form, or as JSON in the POST body.

### Example Usage for format param and Accept header

```sh
curl https://{{ main_host }}/?format=json
curl -H 'Accept: application/json' https://{{ main_host }}/

curl https://{{ main_host }}/?format=yaml 
curl -H 'Accept: application/yaml' https://{{ main_host }}/

curl https://{{ main_host }}/lookup/185.130.44.123?format=yaml 
curl -H 'Accept: application/yaml' https://{{ main_host }}/lookup/185.130.44.123

# Using the HTTPie tool to send a JSON body POST request 
http -p hbHB POST https://{{ main_host }}/lookup/ format=plain addr=185.130.44.56
```

### HTML

At the time of writing, currently only the index page ( `/` ), as well as this page ( `/api/` ) support outputting their
data in HTML format - though `/api/` (this page) is purely a documentation page, and does not have any special functionality 
anyway.

HTML is used by default for the index page, however if needed, you can manually specify that you want HTML output
by either passing `format=html` as a GET/POST (i.e. `/?format=html`) argument, or by ensuring that `text/html`
is the highest priority in your `Accept:` header.

Matching types for `format=` and `Accept:` are:

- `html`
- `text/html`
- `text/x-html`
- `text/xhtml`
- `text/xhtml+xml`
- `applicatiom/html`
- `application/x-html`
- `application/xhtml`
- `application/xhtml+xml`
- `web`
- `page`
- `webpage`

### JSON

The **JSON** format is available as a format option on the following endpoints:

- `/` (index - default format: `html`)
- `/lookup(/<ip>)(/<dtype>)` (IP Lookup - default format: `json`)

Matching types for `format=` and `Accept:` are:

- `json`
- `js`
- `api`
- `text/json`
- `text/x-json`
- `application/json`
- `application/x-json`
- `application/js`


### YAML (YML)

The **YAML** format is available as a format option on the following endpoints:

- `/` (index - default format: `html`)
- `/lookup(/<ip>)(/<dtype>)` (IP Lookup - default format: `json`)

Matching types for `format=` and `Accept:` are:

- `yaml`
- `yml`
- `applicatiom/yaml`
- `applicatiom/yml`
- `applicatiom/x-yaml`
- `applicatiom/x-yml`
- `text/yaml`
- `text/yml`
- `text/x-yaml`
- `text/x-yml`

### Plain Text

The **Plain Text** format is available as a format option on the following endpoints:

- `/` (index - default format: `html`)
- `/lookup(/<ip>)(/<dtype>)` (IP Lookup - default format: `json`)
- `/flat(/<dtype>)` (Simple flat connecting IP lookup for shellscripts - default format: `plain`)

Matching types for `format=` and `Accept:` are:

- `flat`
- `plain`
- `x-plain`
- `plaintext`
- `plain-text`
- `text`
- `text/*`
- `text/plain`
- `text/x-plain`
- `text/plaintext`
- `text/plain-text`
- `application/text`
- `application/plain`
- `application/x-plain`
- `application/plaintext`
- `application/plain-text`

## Index Endpoint

The index endpoint at `/` - by default renders an HTML web page, designed to be read by humans. The HTML page displays
the current IP you're connecting from - directly within the HTML body, while the IPv4/IPv6 sections are populated
using JavaScript via AJAX queries to the JSON format of this endpoint on our v4 and v6-only domains.

Endpoints:

    /
    /index.txt
    /index.yml
    /index.yaml
    /index.json
    /index.html


### Supported Output Formats

- **HTML** (`html`) - This is the DEFAULT used for the index endpoint
- **Plain Text** (`plain`) - Displays information about the IP and User Agent you're connecting from, in plain text. 
                             The plain text output is designed to be easy to parse using standard UNIX utilities
                             such as `grep`, `awk`, `sed`, and/or even just using `IFS=` within shells like bash/zsh.
- **JSON** (`json`) - Displays information about the IP you're connecting from, in JSON format.
- **YAML** (`yaml` / `yml`) - Displays information about the IP you're connecting from, in YAML (YML) format.

### Example Queries

#### JSON Output for Index Endpoint

On URLs which support JSON output, you can either pass the GET parameter `?format=json` - or you can set the `Accept` header so
that `application/json` is the most preferred content requested from the server.

You can query the main site to get information about your system's most preferred IP version, or if the client you're querying
with (e.g. curl with `-4` or `-6`) allows specifying the IP version, then you can select an IP version using your client.

```sh
curl https://{{ main_host }}/?format=json

# Alternative - send the header 'Accept: application/json'
curl -H 'Accept: application/json' https://{{ main_host }}/

# Make the request using IPv4
curl -4 https://{{ main_host }}/?format=json
# Make the request using IPv6
curl -6 https://{{ main_host }}/?format=json
```

**Example Output:**

```json
{
    "error": false,
    "geo": {
        "as_name": "Privex Inc.",
        "as_number": 210083,
        "city": "Stockholm",
        "country": "Sweden",
        "country_code": "SE",
        "error": false,
        "ip_address": "2a07:e01:123::456",
        "lat": 59.3333,
        "long": 18.05,
        "network": "2a07:e01::/32",
        "postcode": "173 11"
    },
    "hostname": "",
    "ip": "2a07:e01:123::456",
    "ip_type": "ipv6",
    "ip_valid": true,
    "messages": [],
    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:89.0) Gecko/20100101 Firefox/89.0"
}
```

Alternatively, you can query our IPv4-only / IPv6-only domain to force your client to use a specific IP version to obtain the
results:

```sh
curl https://{{ v4_host }}/?format=json

curl https://{{ v6_host }}/?format=json
```

#### Plain Output for Index Endpoint

You can request plain text output from our index page using `?format=plain` - or you can set your `Accept` to
prioritise `text/plain`.

```sh
curl https://{{ main_host }}/?format=plain

# Alternative - send the header 'Accept: text/plain'
curl -H 'Accept: text/plain' https://{{ main_host }}/
```
`
Result:

```yml
IP: 2a07:e01:123::456
Version: ipv6
Hostname:
UserAgent: HTTPie/2.0.0
Country: Sweden
CountryCode: SE
City: Stockholm
Postcode: 173 11
Lat: 59.3333
Long: 18.05
ASNum: 210083
ASName: Privex Inc.
Network: 2a07:e01::/32
```

## Lookup Endpoint

The **lookup endpoint** allows you to query General + GeoIP information about any arbitrary IPv4/IPv6 address.

Endpoints:

    /lookup/
    /lookup.yml/
    /lookup.yaml/
    /lookup.json/
    /lookup.txt/
    /lookup/<addr>/(<type>/)
    /lookup.yml/<addr>/(<type>/)
    /lookup.yaml/<addr>/(<type>/)
    /lookup.json/<addr>/(<type>/)
    /lookup.txt/<addr>/(<type>/)

### Supported Output Formats

- **JSON** (`json`) - This is the DEFAULT used for the lookup endpoint. Displays information about the IP you're looking up, in
  JSON format.
- **Plain Text** (`plain`) - Displays information about the IP and User Agent you're looking up, in plain text. The plain
  text output is designed to be easy to parse using standard UNIX utilities such as `grep`, `awk`, `sed`, and/or even just
  using `IFS=` within shells like bash/zsh.

- **YAML** (`yaml` / `yml`) - Displays information about the IP you're looking up, in YAML (YML) format.

### Example Queries

#### Standard GET request

Command:

```sh
user@privex-example ~ $ http -p hbHB GET https://{{ main_host }}/lookup/
```

Result:

```http
GET /lookup/ HTTP/1.1

HTTP/1.0 200 OK
Content-Length: 471
Content-Type: application/json

{
    "error": false,
    "geo": {
        "as_name": "Privex Inc.",
        "as_number": 210083,
        "city": "Stockholm",
        "country": "Sweden",
        "country_code": "SE",
        "error": false,
        "ip_address": "2a07:e01:123::456",
        "lat": 59.3333,
        "long": 18.05,
        "network": "2a07:e01::/32",
        "postcode": "173 11"
    },
    "hostname": "",
    "ip": "2a07:e01:123::456",
    "ip_type": "ipv6",
    "ip_valid": false,
    "messages": [],
    "ua": "HTTPie/2.0.0"
}
```

#### GET Request with IP in URI + yml format

Command:

```sh
user@privex-example ~ $ http -p hbHB GET https://{{ main_host }}/lookup/185.130.46.70?format=yml
```

```http
GET /lookup/185.130.46.70?format=yml HTTP/1.1

HTTP/1.0 200 OK
Content-Length: 352
Content-Type: application/yaml

error: false
geo:
  as_name: Privex Inc.
  as_number: 210083
  city: Tokyo
  country: Japan
  country_code: JP
  error: false
  ip_address: 185.130.46.70
  lat: 35.6887
  long: 139.745
  network: 185.130.46.0/24
  postcode: 102-0082
hostname: 185.130.46.70.static.privex.cc
ip: 185.130.46.70
ip_type: ipv4
ip_valid: false
messages: []
ua: HTTPie/2.0.0
```

#### POST Request with IP in JSON body + plain format


Command:

```sh
user@privex-example ~ $  http -p hbHB POST https://{{ main_host }}/lookup.txt/ ip=185.130.44.56
```

```http
POST /lookup.txt/ HTTP/1.1
Accept: application/json, */*
Content-Type: application/json

{
    "ip": "185.130.44.56"
}

HTTP/1.0 200 OK
Content-Length: 247
Content-Type: text/plain

IP: 185.130.44.56
Version: ipv4
Hostname: 185.130.44.56.static.privex.cc
UserAgent: HTTPie/2.0.0
Country: Sweden
CountryCode: SE
City: Stockholm
Postcode: 173 11
Lat: 59.3333
Long: 18.05
ASNum: 210083
ASName: Privex Inc.
Network: 185.130.44.0/23
```


## Flat Type Summaries

These **Flat Types** can be used both with `/flat/<type>` as well as `/lookup/<ip>`

- `ip` / `addr` / `address` / `ip_address` - Get IPv4/v6 address
- `dns` / `rdns` / `reverse` / `host` / `hostname` - Get the Reverse DNS (rDNS) hostname for the IP address
- `version` / `type` / `ipv` / `ipver` / `ipversion` / `ip_version` - Outputs either `ipv4` or `ipv6` depending on whether you're
  connecting from / looking up an IPv4 or IPv6 address.
- `ua` / `agent` / `useragent` / `user_agent` - Get client/browser User Agent
- `country` / `region` - Get the name of the country where the IP appears to be located
- `country_code` / `region_code` / `country-code` / `region-code` / `code` - Get the two-letter country code where the IP appears
  to be located
- `city` / `area` - Get the name of the city where the IP appears to be located
- `as` / `asn` / `asnum` / `asnumber` / `isp_number` / `isp_asn` - Get the ASN (Autonomous System Number) of the network which
  your IP appears to belong to.
- `asname` / `isp` / `as_name` / `isp_name` / `ispname` - Get the name of the ISP / AS of which your IP appears to belong to.
- `asfull` / `fullas` / `asnfull` / `ispfull` / `fullisp` / `asinfo` / `asninfo` / `asn_info` / `ispinfo` / `isp_info` - Get the
  name of the ISP/AS your IP appears to belong to, as well as the AS number (with `AS` prefix), separated by a newline.
- `loc` / `locate` / `location` / `countrycity` / `citycountry` / `country_city` / `city_country` - The city, zip/postcode, and
  country, in a single line formatted like an address.
- `post` / `postal` / `postcode` / `post_code` / `zip` / `zipcode` / `zip_code` - The ZIP / Postcode where your IP appears to be
  located within the country/city.
- `lat` / `latitude` - The **latitude** co-ordinate, which determines the north/south position in the world.
- `lon` / `long` / `longitude` - The **longitude** co-ordinate, which determines the east/west position in the world.
- `latlon` /` latlong` / `latitudelongitude` / `pos` / `position` / `cord` / `coord` / `coords`
  / `coordinates` / `co-ordinates` - The **latitude** AND **longitude**, separated by a comma and space.
- `all` / `full` / `info` / `information` - All available information about

## Flat Endpoint

We also have the "flat" endpoint:

    /flat(/<type>)

This is designed for use in shellscripts (bash/zsh/etc.), and other kinds of situations where you might not be able to parse
JSON/YML/etc.




### Get just your IP address

```sh
user@host ~ $ curl https://{{ main_host }}/flat
2a07:e01:123::456

user@host ~ $ curl -4 https://{{ main_host }}/flat
185.130.44.140
```

### Get just your User Agent

```sh
user@host ~ $ curl https://{{ main_host }}/flat/ua
curl/7.54.0
```

### Get just the Country (GeoIP) of your IP address

```sh
user@host ~ $ curl https://{{ main_host }}/flat/country
Sweden
```

### Get just the City (GeoIP) of your IP address

```sh
user@host ~ $ curl https://{{ main_host }}/flat/city
Stockholm
```

### Get your full GeoIP location, formatted like an address

```sh
user@host ~ $ curl https://{{ main_host }}/flat/location
Stockholm, 173 11, Sweden
```

### Get your GeoIP location co-ordinates, returned as latitude, longitude

```sh
user@host ~ $ curl https://{{ main_host }}/flat/pos
59.3333, 18.0500
```

### Get your ISP/ASN name and their AS number, separated by a newline

```sh
user@host ~ $ curl https://{{ main_host }}/flat/asninfo
Privex Inc.
AS210083
```
