/**
 * Main Javascript file for Privex's IP and browser information web application.
 * 
 * (C) 2019 Privex Inc.    https://www.privex.io/
 * 
 * Released under the GNU AGPL v3 open source license.
 * 
 */


function mkflag(code, country) {
    return `<img class="flag" src="/static/flags/${code.toLowerCase()}.gif" alt="${country} Flag" />`
}

function load_addr(ver, host) {
    console.log(`Requesting IPv${ver} info from ${host}`);
    $.getJSON(host).then(function(data) {
        var ip = 'Unknown', isp = 'Unknown', country = 'Unknown', city = 'Unknown';
        console.log(`Loaded IPv${ver} data:`, data);
        if('ip' in data) ip = data.ip;
        if('geo' in data) {
            var g = data.geo;
            if ('as_name' in g) isp = `${g.as_name} (ASN ${g.as_number})`;
            if ('country' in g) country = `${mkflag(g.country_code, g.country)} ${g.country}`;
            if ('city' in g) city = g.city;
        } 
        $(`#addr-v${ver}`).html(ip);
        $(`#addr-v${ver}-isp`).html(isp);
        $(`#addr-v${ver}-country`).html(country);
        $(`#addr-v${ver}-city`).html(city);
    }).fail(function(data) {
        console.error(`Couldn't load IPv${ver} address information from ${host}. Data is:`, data);
        $(`#ipv${ver}-info`).hide();
        $(`#ipv${ver}-info-fail`).show();
    });
}

$(function() {
    load_addr('4', v4_host);
    load_addr('6', v6_host);

    // console.log(`Requesting IPv4 info from ${v4_host}`);
    // $.getJSON(v4_host).then(function(data) {
    //     var ip = 'Unknown', isp = 'Unknown', country = 'Unknown';
    //     console.log('Loaded IPv4 data:', data);
    //     if('ip' in data) ip = data.ip;
    //     if('geo' in data) {
    //         var g = data.geo;
    //         if ('as_name' in g) isp = `${g.as_name} (ASN ${g.as_number})`;
    //         if ('country' in g) country = `${mkflag(g.country_code, g.country)} ${g.country}`;
    //         if ('city' in g) city = g.city;
    //     } 
    //     $('#addr-v4').html(ip);
    //     $('#addr-v4-isp').html(isp);
    //     $('#addr-v4-country').html(country);
    //     $('#addr-v4-city').html(city);
    // }).fail(function(data) {
    //     console.error(`Couldn't load IPv4 address information from ${v4_host}. Data is:`, data);
    //     $('#ipv4-info').hide();
    //     $('#ipv4-info-fail').show();
    // });

    // console.log(`Requesting IPv6 info from ${v6_host}`);
    // $.getJSON(v6_host).then(function(data) {
    //     var ip = 'Unknown', isp = 'Unknown', country = 'Unknown', city = 'Unknown';
    //     console.log('Loaded IPv6 data:', data);
    //     if('ip' in data) ip = data.ip;
    //     if('geo' in data) {
    //         var g = data.geo;
    //         if ('as_name' in g) isp = `${g.as_name} (ASN ${g.as_number})`;
    //         if ('country' in g) country = `${mkflag(g.country_code, g.country)} ${g.country}`;
    //         if ('city' in g) city = g.city;
    //     } 
    //     $('#addr-v6').html(ip);
    //     $('#addr-v6-isp').html(isp);
    //     $('#addr-v6-country').html(country);
    //     $('#addr-v6-city').html(city);
    // }).fail(function(data) {
    //     console.error(`Couldn't load IPv6 address information from ${v6_host}. Data is:`, data);
    //     $('#ipv6-info').hide();
    //     $('#ipv6-info-fail').show();
    // });
    $('.ui.accordion').accordion('close', 0);
    $('.ui.accordion').accordion('close', 1);

})
