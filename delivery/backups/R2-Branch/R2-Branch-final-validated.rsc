# 2026-07-26 21:26:15 by RouterOS 7.22.1
# system id = waOMd4TLR6P
#
#
#
/interface ethernet
set [ find default-name=ether1 ] comment="WAN - UTM Shared Network"
set [ find default-name=ether2 ] comment="LAN - Branch Network"
/interface wireguard
add comment="Secure site-to-site VPN to HQ" listen-port=13232 mtu=1420 name=\
    wg-s2s
/interface list
add comment="Untrusted Internet side" name=WAN
add comment="Trusted HQ side" name=LAN
add comment="Trusted VPN interfaces" name=VPN
/ip pool
add name=branch-dhcp-pool ranges=10.30.30.100-10.30.30.200
/interface list member
add interface=ether1 list=WAN
add interface=ether2 list=LAN
add interface=wg-s2s list=VPN
/interface wireguard peers
add allowed-address=10.255.255.1/32,10.10.10.0/24 comment=\
    "R1 HQ site-to-site" endpoint-address=192.168.64.2 endpoint-port=13232 \
    interface=wg-s2s name=hq-r1 persistent-keepalive=25s public-key=\
    "0qeVu6DeQgx37OERWmdCZ33hhWt5LyT0yOVWKSc1m0k="
/ip address
add address=10.30.30.1/24 comment="Branch LAN Gateway" interface=ether2 \
    network=10.30.30.0
add address=10.255.255.2/30 comment="S2S transit Branch" interface=wg-s2s \
    network=10.255.255.0
/ip dhcp-client
add dhcp-options=hostname interface=ether1 name=client1
/ip dhcp-server
add address-pool=branch-dhcp-pool interface=ether2 lease-time=10m name=\
    branch-dhcp
/ip dhcp-server network
add address=10.30.30.0/24 dns-server=10.30.30.1 gateway=10.30.30.1
/ip dns
set allow-remote-requests=yes
/ip firewall filter
add action=accept chain=input comment="INPUT allow UTM host management" \
    in-interface=ether1 src-address=192.168.64.1
add action=accept chain=input comment="INPUT accept established related" \
    connection-state=established,related,untracked
add action=drop chain=input comment="INPUT drop invalid" connection-state=\
    invalid
add action=accept chain=input comment="INPUT allow WAN DHCP client" dst-port=\
    68 in-interface=ether1 protocol=udp src-port=67
add action=accept chain=input comment="INPUT allow limited ICMP" limit=\
    10,20:packet protocol=icmp
add action=accept chain=input comment="INPUT allow trusted Branch LAN" \
    in-interface=ether2 src-address=10.30.30.0/24
add action=accept chain=input comment="INPUT allow WireGuard site-to-site" \
    dst-port=13232 in-interface=ether1 protocol=udp
add action=accept chain=input comment="INPUT allow HQ via site-to-site" \
    in-interface=wg-s2s src-address=10.10.10.0/24
add action=drop chain=input comment="INPUT default deny"
add action=accept chain=forward comment="FORWARD accept established related" \
    connection-state=established,related,untracked
add action=drop chain=forward comment="FORWARD drop invalid" \
    connection-state=invalid
add action=accept chain=forward comment=\
    "FORWARD allow Branch LAN to Internet" in-interface=ether2 out-interface=\
    ether1 src-address=10.30.30.0/24
add action=accept chain=forward comment="FORWARD Branch LAN to HQ LAN" \
    dst-address=10.10.10.0/24 in-interface=ether2 out-interface=wg-s2s \
    src-address=10.30.30.0/24
add action=accept chain=forward comment="FORWARD HQ LAN to Branch LAN" \
    dst-address=10.30.30.0/24 in-interface=wg-s2s out-interface=ether2 \
    src-address=10.10.10.0/24
add action=drop chain=forward comment="FORWARD default deny"
/ip firewall nat
add action=masquerade chain=srcnat comment="Branch LAN to Internet" \
    out-interface=ether1 src-address=10.30.30.0/24
/ip route
add comment="Route to HQ LAN via WireGuard" dst-address=10.10.10.0/24 \
    gateway=wg-s2s
/ip service
set ftp disabled=yes
set telnet disabled=yes
set reverse-proxy disabled=yes
set api disabled=yes
set api-ssl disabled=yes
/system identity
set name=R2-Branch
#error exporting "/system/routerboard/mode-button"
#error exporting "/system/routerboard/reset-button"
#error exporting "/system/routerboard/wps-button"
