# 2026-07-26 21:26:06 by RouterOS 7.22.1
# system id = Ppmiwc7ZnLM
#
#
#
/interface ethernet
set [ find default-name=ether1 ] comment="WAN - UTM shared Network\
    \n"
set [ find default-name=ether2 ] comment="LAN - HQ Network"
/interface wireguard
add comment="Secure remote employees VPN" listen-port=13231 mtu=1420 name=\
    wg-employees
add comment="Secure site-to-site VPN to Branch" listen-port=13232 mtu=1420 \
    name=wg-s2s
/interface list
add comment="Untrusted Internet side" name=WAN
add comment="Trusted HQ side" name=LAN
add comment="Trusted VPN interfaces" name=VPN
/ip pool
add name=dhcp_pool0 ranges=10.10.10.100-10.10.10.200
/ip dhcp-server
add address-pool=dhcp_pool0 interface=ether2 lease-time=10m name=dhcp1
/interface list member
add interface=ether1 list=WAN
add interface=ether2 list=LAN
add interface=wg-employees list=VPN
add interface=wg-s2s list=VPN
/interface wireguard peers
add allowed-address=10.20.20.2/32 client-address=10.20.20.2/32 \
    client-allowed-address=0.0.0.0/0 client-dns=10.20.20.1 client-endpoint=\
    192.168.64.2:13231 client-keepalive=25s comment=\
    "Employee 01 remote access" interface=wg-employees name=employee-01 \
    public-key="tsgELVBpmzMsdDplmvjhHmb/R0fHo4eqL6kW3jNFYVM=" responder=yes
add allowed-address=10.255.255.2/32,10.30.30.0/24 comment=\
    "R2 Branch site-to-site" endpoint-address=192.168.64.4 endpoint-port=\
    13232 interface=wg-s2s name=branch-r2 persistent-keepalive=25s \
    public-key="7v/SX/cuU/gQP5auoUpkZY7azD9tc7kpz7/5CYsATGI="
/ip address
add address=10.10.10.1/24 comment="HQ LAN Gateway" interface=ether2 network=\
    10.10.10.0
add address=10.20.20.1/24 comment="Employees VPN gateway" interface=\
    wg-employees network=10.20.20.0
add address=10.255.255.1/30 comment="S2S transit HQ" interface=wg-s2s \
    network=10.255.255.0
/ip dhcp-client
add interface=ether1 name=client1
/ip dhcp-server network
add address=10.10.10.0/24 dns-server=10.10.10.1 gateway=10.10.10.1
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
add action=accept chain=input comment="INPUT allow trusted HQ LAN" \
    in-interface=ether2 src-address=10.10.10.0/24
add action=accept chain=input comment="INPUT allow WireGuard employees" \
    dst-port=13231 in-interface=ether1 protocol=udp
add action=accept chain=input comment="INPUT allow employees VPN to router" \
    in-interface=wg-employees src-address=10.20.20.0/24
add action=accept chain=input comment="INPUT allow WireGuard site-to-site" \
    dst-port=13232 in-interface=ether1 protocol=udp
add action=accept chain=input comment="INPUT allow Branch via site-to-site" \
    in-interface=wg-s2s
add action=drop chain=input comment="INPUT default deny"
add action=accept chain=forward comment="FORWARD accept established related" \
    connection-state=established,related,untracked
add action=drop chain=forward comment="FORWARD drop invalid" \
    connection-state=invalid
add action=accept chain=forward comment="FORWARD allow HQ LAN to Internet" \
    in-interface=ether2 out-interface=ether1 src-address=10.10.10.0/24
add action=accept chain=forward comment="FORWARD employees VPN to HQ LAN" \
    dst-address=10.10.10.0/24 in-interface=wg-employees out-interface=ether2 \
    src-address=10.20.20.0/24
add action=accept chain=forward comment="FORWARD employees VPN to Internet" \
    in-interface=wg-employees out-interface=ether1 src-address=10.20.20.0/24
add action=accept chain=forward comment="FORWARD HQ LAN to Branch LAN" \
    dst-address=10.30.30.0/24 in-interface=ether2 out-interface=wg-s2s \
    src-address=10.10.10.0/24
add action=accept chain=forward comment="FORWARD Branch LAN to HQ LAN" \
    dst-address=10.10.10.0/24 in-interface=wg-s2s out-interface=ether2 \
    src-address=10.30.30.0/24
add action=drop chain=forward comment="FORWARD default deny"
/ip firewall nat
add action=masquerade chain=srcnat comment="HQ LAN to Internet" \
    out-interface=ether1 src-address=10.10.10.0/24
add action=masquerade chain=srcnat comment="Employees VPN to Internet" \
    out-interface=ether1 src-address=10.20.20.0/24
/ip route
add comment="Route to Branch LAN via WireGuard" dst-address=10.30.30.0/24 \
    gateway=wg-s2s
/ip service
set ftp disabled=yes
set telnet disabled=yes
set reverse-proxy disabled=yes
set api disabled=yes
set api-ssl disabled=yes
/system identity
set name=R1-HQ
#error exporting "/system/routerboard/mode-button"
#error exporting "/system/routerboard/reset-button"
#error exporting "/system/routerboard/wps-button"
