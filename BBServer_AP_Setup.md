# Instructions for setting up AP and WLAN on RPi3

Instructions taken from [this stackexchange page](https://raspberrypi.stackexchange.com/questions/89803/access-point-as-wifi-router-repeater-optional-with-bridge)

<p>We are talking about an access point together with a wireless client connection on interface <strong>wlan0</strong> to another wifi network (wlan repeater) or an internet router.</p>
<p>If you want an access point together with an ethernet interface <strong>eth0</strong> for a wired uplink to a switch or an internet router then look at <a href="https://raspberrypi.stackexchange.com/q/88214/79866">Setting up a Raspberry Pi as an access point - the easy way</a>.</p>
<p>Tested on a Raspberry Pi 4B with<br />
<a href="https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2020-08-24/" rel="nofollow noreferrer">Raspberry Pi OS (32-bit) with desktop 2020-08-20</a> updated on 2020-09-01.<br />
<a href="https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2020-05-28/" rel="nofollow noreferrer">Raspberry Pi OS (32-bit) with desktop 2020-05-27</a> updated on 2020-06-11.<br />
<a href="https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2020-02-14/" rel="nofollow noreferrer">Raspbian Buster Lite 2020-02-13</a> updated on 2020-03-03.<br />
Updates done with <code>sudo apt update &amp;&amp; sudo apt full-upgrade &amp;&amp; sudo reboot</code>.</p>
<p>Here you will find the <a href="https://raspberrypi.stackexchange.com/revisions/89804/26">last tested revision for Raspbian Stretch Lite</a>.</p>
<p><strong>IMPORTANT UPDATE</strong> on 2020-09-02:<br />
I have found that the image versions of the <strong>Raspberry Pi OS</strong> come with an unstable firmware for the built-in WiFi device. For further information look at my bug report at <a href="https://github.com/raspberrypi/firmware/issues/1463" rel="nofollow noreferrer">WiFi firmware brcmfmac crashes when using virtual AP interface</a>. The last stable is <a href="http://archive.raspberrypi.org/debian/pool/main/f/firmware-nonfree/" rel="nofollow noreferrer">firmware-brcm80211_20190114-1+rpt4_all.deb</a> comming with image <strong>Raspbian Buster Lite 2020-02-13</strong>.</p>
<p>So we have to downgrade the WiFi firmware to this stable version as long as the bug isn't fixed. After flashing the <em>Raspberry Pi OS</em> image with update/full-upgrade, follow this to do downgrade:</p>

```
rpi ~$ wget http://archive.raspberrypi.org/debian/pool/main/f/firmware-nonfree/firmware-brcm80211_20190114-1+rpt4_all.deb
rpi ~$ sudo dpkg --purge firmware-brcm80211
rpi ~$ sudo dpkg --install firmware-brcm80211_20190114-1+rpt4_all.deb
rpi ~$ sudo apt-mark hold firmware-brcm80211
rpi ~$ sudo systemctl reboot
```

<hr />
<p>The Raspberry Pi is able to work as a wireless hotspot and simultaneously connect to another hotspot as a client. But the wifi device on the RasPi has a general limitation. The client connection cannot be bridged because lack of WDS (wireless distribution system) that is needed for bridging on the wireless. For further information look at <a href="https://raspberrypi.stackexchange.com/a/81518/79866">Raspberry Pi WiFi to Ethernet Bridge for a server?</a>. So we can only use routing for the wifi client connection to the internet router. But the wifi hotspot and the wired ethernet port can be bridged so all devices on wifi and the wired port can have the same broadcast domain on its common subnet.</p>
<p>I assume that you already have a connection to the internet. All commands can simply be copied and pasted to the command line of the RasPi. The blocks with EOF you can select from <code>cat</code> incl. the last <code>EOF</code> and paste it to the RasPis command line. With <em>Enter</em> it will be copied to a file without the delimiter EOF.</p>
<p>We will first setup a <strong>wifi repeater</strong> so if anyone only needs this he can stop setup at this point and use it. For those who need a <strong>bridged ethernet port</strong> with the wifi access point can continue with setting it up.</p>
<p>I use <em>systemd-networkd</em> for reasons. For the impatient first only the Setup.</p>
<hr />
<h2>&diams; Setup wifi repeater</h2>
<p>Example for this setup:</p>

```
                 wifi                         wifi uplink         wan
mobile-phone <~.~.~.~.~> (ap@wlan0)RPi(wlan0) <.~.~.~.~.> router <───> INTERNET
            ╲             ╱               ╲
           (dhcp    192.168.4.1          (dhcp
         from RPi)                    from router)
```


## Step 1: Update , upgrade and install hostapd

```
rpi ~$ sudo -Es   # if not already done
rpi ~# apt-get -y update # if not already done
rpi ~# apt-get -y upgrade #if not already done
rpi ~# apt install hostapd
rpi ~# systemctl reboot
```

Unlike in the stackexchange thread, hostapd is installed before systemd-networkd, as tests showed that the systemd-networkd step sometimes prevented an internet connection until fully set up. Hostapd will fail when it tries to run immediately after installation - this is fine.


## Step 2: setup systemd-networkd

run the following to use systemd-networkd instead of dhcpcd. Explanation of what this is doing can be found at <a href="https://raspberrypi.stackexchange.com/a/108593/79866">Use systemd-networkd for general networking</a>

```
# deinstall classic networking
pi@raspberrypi:~ $ sudo -Es   # if not already done
root@raspberrypi:~ # apt --autoremove purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
root@raspberrypi:~ # apt-mark hold ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog raspberrypi-net-mods openresolv
root@raspberrypi:~ # rm -r /etc/network /etc/dhcp

# setup/enable systemd-resolved and systemd-networkd
root@raspberrypi:~ # apt --autoremove purge avahi-daemon
root@raspberrypi:~ # apt-mark hold avahi-daemon libnss-mdns
root@raspberrypi:~ # apt install libnss-resolve
root@raspberrypi:~ # ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
root@raspberrypi:~ # systemctl enable systemd-networkd.service systemd-resolved.service
root@raspberrypi:~ # exit
pi@raspberrypi:~ $
```

<h3>Step 3: Setup hostapd for the access point</h3>

<p>Create this file with your settings for <code>ssid=</code>, <code>country_code=</code> and <code>wpa_passphrase=</code>. As <code>channel=</code> select the same channel <em>wpa_supplicant</em> with <strong>wlan0</strong> will connect to your internet router.<br />

<strong>ATTENTION! This is a restriction from the hardware. `hostapd` will always set the channel to the same value than from the client connection, no matter what you set here.</strong>

If you need different channels then you have to use an additional USB/WiFi dongle.</p>

```
rpi ~# cat > /etc/hostapd/hostapd.conf <<EOF
driver=nl80211
ssid=BiBServer_id
country_code=GB
hw_mode=g
channel=1
auth_algs=1
wpa=2
wpa_passphrase=verySecretPassword
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

rpi ~# chmod 600 /etc/hostapd/hostapd.conf
```

<p>Create a service for the accesspoint with hostapd:</p>

```
rpi ~# systemctl edit --force --full accesspoint@.service
```
<p>In the empty editor insert these statements, save them and quit the editor:</p>

```
[Unit]
Description=accesspoint with hostapd (interface-specific version)
Wants=wpa_supplicant@%i.service

[Service]
ExecStartPre=/sbin/iw dev %i interface add ap@%i type __ap
ExecStart=/usr/sbin/hostapd -i ap@%i /etc/hostapd/hostapd.conf
ExecStopPost=-/sbin/iw dev ap@%i del

[Install]
WantedBy=sys-subsystem-net-devices-%i.device
```
<p>Enable the service:</p>

```
rpi ~# systemctl enable accesspoint@wlan0.service
rpi ~# rfkill unblock wlan
```

<h3>Step 4: setup wpa_supplicant for client connection</h3>

<p>Create this file with your settings for <code>country=</code>, <code>ssid=</code> and <code>psk=</code> and enable it:</p>

```
rpi ~# cat > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf <<EOF
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="School_Wifi";
    psk="School_Wifi_Passphrase";
    key_mgmt=WPA-PSK   # see ref (4)
}
EOF

rpi ~# chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
rpi ~# systemctl disable wpa_supplicant.service
```

<p>Extend wpa_supplicant with:</p>

```
rpi ~# systemctl edit wpa_supplicant@wlan0.service
```
<p>In the empty editor insert these statements. Save it and quit the editor:</p>

```
[Unit]
BindsTo=accesspoint@%i.service
After=accesspoint@%i.service
```

<h3>Step 5: setup static interfaces</h3>

<p>Create these files:</p>

```
rpi ~# cat > /etc/systemd/network/08-wifi.network <<EOF
[Match]
Name=wl*
[Network]
LLMNR=no
MulticastDNS=yes
# If you need a static ip address, then toggle commenting next four lines (example)
DHCP=yes
#Address=192.168.50.60/24
#Gateway=192.168.50.1
#DNS=84.200.69.80 1.1.1.1
EOF
```
<p>For those who want a bridge, do not need the next file and must continue with <strong>Setup bridge</strong>.</p>

```
rpi ~# cat > /etc/systemd/network/12-ap.network <<EOF
[Match]
Name=ap@*
[Network]
LLMNR=no
MulticastDNS=yes
IPMasquerade=yes
Address=192.168.4.1/24
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
EOF
```
<p>Setup a wifi repeater without bridge is finished. You must<br />
Reboot.</p>

<hr />
<h2>&diams; Setup bridge</h2>
<p><strong>Setup wifi repeater</strong> as described above.</p>
<p>Example for this setup:</p>

```
          (dhcp
        from RPi)        bridge
           ╱    wifi    ┌──────┐
mobile-phone <~.~.~.~.> │(ap@) │           wifi uplink         wan
                        │   br0│RPi(wlan0) <.~.~.~.~.> router <───> INTERNET
      laptop <────────> |(eth0)│╲       ╲
           ╲    wired   └──────┘╱      (dhcp
         (dhcp           192.168.4.1   from router)
       from RPi)
```
<h3>Step 6: configure hostapd for a bridge</h3>
<p>Add a line <code>bridge=br0</code> to <em>/etc/hostapd/hostapd.conf</em> with:</p>

```
rpi ~# echo 'bridge=br0' >> /etc/hostapd/hostapd.conf
```
<h3>Step 7: setup wpa_supplicant for a bridge</h3>
<p>Extend wpa_supplicant with:</p>

```
rpi ~# systemctl edit wpa_supplicant@wlan0.service
```
<p>In the editor append lines so it looks like the following. Have attention to the minus sign after equal <code>=-</code> on some statements. Save it and quit the editor:</p>

```
[Unit]
BindsTo=accesspoint@%i.service
After=accesspoint@%i.service

[Service]
ExecStartPost=/lib/systemd/systemd-networkd-wait-online --interface=%i --timeout=60 --quiet
ExecStartPost=/bin/ip link set ap@%i up
ExecStopPost=-/bin/ip link set ap@%i up
```
<p>Please note that <code>ExecStopPost=-/bin/ip link set ap@%i up</code> is not a typo. On stopping wpa_supplicant, interface <strong>ap@wlan0</strong> must be set <strong>up</strong> again as described in section <strong>Details - wpa_supplicant for bridge (Step 7)</strong>.</p>
<h3>Step 8: setup static interfaces</h3>
<p>For a bridge <strong>ap@wlan</strong> is dynamically created. So create these files:</p>

```
rpi ~# cat > /etc/systemd/network/02-br0.netdev <<EOF
[NetDev]
Name=br0
Kind=bridge
EOF

rpi ~# cat > /etc/systemd/network/04-eth0.network <<EOF
[Match]
Name=eth0
[Network]
Bridge=br0
EOF

rpi ~# cat > /etc/systemd/network/16-br0_up.network <<EOF
[Match]
Name=br0
[Network]
IPMasquerade=yes
Address=192.168.4.1/24
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
EOF
```
<p>Reboot.<br />
That's it.</p>
<hr />
<h2>&diams; Details</h2>
<h3>General</h3>
<p>One problem is that we want to use the same device for a wifi client and for an access point. This must be supported by the wifi hardware. We can check this with</p>

```
rpi ~$ sudo iw list | grep -A4 "valid interface combinations:""
        valid interface combinations:
             * #{ managed } <= 1, #{ P2P-device } <= 1, #{ P2P-client, P2P-GO } <= 1,
               total <= 3, #channels <= 2
             * #{ managed } <= 1, #{ AP } <= 1, #{ P2P-client } <= 1, #{ P2P-device } <= 1,
               total <= 4, #channels <= 1
```
<p>The important part is <code> #{ managed } &lt;= 1, #{ AP } &lt;= 1,</code> but you can also see that <strong>this is only possible on one channel</strong>.</p>
<p>I've found that we have to setup this in sequence, otherwise, it won't work. If other applications bind to the wifi port it cannot be set.</p>
<ol>
<li><strong>create a virtual interface <code>ap@wlan0</code> for the access point</strong></li>
<li><strong>start access point daemon <code>hostapd</code> using interface <code>ap@wlan0</code></strong></li>
<li><strong>start <code>wpa_supplicant</code> for wifi client using interface <code>wlan0</code></strong></li>
</ol>
<p>This order restricts the whole setup. It isn't possible to start <em>hostapd</em> when <em>wpa_supplicant</em> is running. You must first stop <em>wpa_supplicant</em> and then start <em>hostapd</em> and <em>wpa_supplicant</em> in this order. This is due to the WiFi driver <code>brcmfmac</code>.</p>
<p>Another quirk is that <em>wpa_supplicant</em> disables the interface <strong>ap@wlan0</strong> when it is managed, no matter if it starts or stops. So even after a start from <em>wpa_supplicant</em>, we have to enable <strong>ap@wlan0</strong> again.</p>
<p>Here are mainly four components involved: virtual interface <strong>ap@wlan0</strong>, <em>hostapd</em>, <em>wpa_supplicant</em>, and setup the bridge.</p>
<h3>hostapd (Step 3)</h3>
<p>This is the normal setup you will find all over the web. Please set the channel to the same value then <strong>wlan0</strong> is connected to the wifi from your router. It is the restriction from the hardware and may avoid confusion with channel settings. <em>hostapd</em> will always set the channel to the same value than from the client connection, no matter what you set here.</p>
<p>Please use a passphrase that is long enough, I would say at least with 8 characters. It was told that 4 characters are too small and hostapd will refuse to accept connections. You will not find the access point <strong>RPiNet</strong> on your mobile phone (thanks to <a href="https://raspberrypi.stackexchange.com/users/91016/leo">@Leo</a>).</p>
<p>We do not need to unmask the hostapd.service as described at <code>/usr/share/doc/hostapd/README.Debian</code> because we create our own <code>accesspoint@.service</code> for hostapd.</p>
<p>In this service the interface <strong>ap@wlan0</strong> is created before starting <em>hostapd</em>. This is respected to the starting order. Because <strong>ap@wlan0</strong> is bound to <strong>wlan0</strong> it gets the same mac address. You may consider to give it a unique mac address but that's not a good idea. On the network is only seen the mac address from <strong>wlan0</strong>. If you give <strong>ap@wlan0</strong> its own mac address then it is not seen on the network for arp requests and the IP address for connections to <strong>ap@wlan0</strong> is not found and gets stuck. You have to set <strong>ap@wlan0</strong> to promiscuous mode to get it to work then.</p>
<p>After stopped <em>hostapd</em> then <strong>ap@wlan0</strong> is also deleted so it can be created again on the next start of <em>hostapd</em>.</p>
<h3>wpa_supplicant (Step 4)</h3>
<p>Setting up <em>wpa_supplicant</em> for <strong>wlan0</strong> we do as usual. You may consider to disable p2p with <code>p2p_disabled=1</code> in <code>/etc/wpa_supplicant/wpa_supplicant-wlan0.conf</code> to avoid to get the unneeded confusing P2P-device seen with <code>iw dev</code>. Don't do that in this configuration with a virtual AP interface (e.g. ap@wlan0). It confuses wpa_supplicant and it will immediately disconnect from the uplink router when it has just connected to it. It endless connect and disconnect.</p>
<p>Its extended unit is to strictly bind <em>wpa_supplicant</em> to <em>hostapd</em> so it will start and stop with it in the right order. We do it because running <em>wpa_supplicant</em> without <em>hostapd</em> is very complicated and may result in a total crash of the <em>brcmfmac</em> wifi driver, I have seen that on my tests.</p>
<h3>Setup static interfaces (Step 5)</h3>
<p>Here we define interface <strong>wlan0</strong> and the virtual interface <strong>ap@wlan0</strong> we need for a wifi repeater. For <strong>wlan0</strong> we get an IP address by DHCP from the internet router. Optional you can set a static IP address, but then you also have to define all other settings like gateway and DNS server because you don't get them anymore from the DHCP server.</p>
<p>Interface <strong>ap@wlan0</strong> needs a static IP address because it is the access point and the source of the DHCP server for the wifi network. There is no need that clients, connected to the internet router, must also connect to clients on the access point. So we can use NAT  (IPMasquerade=yes) that simplifies setup a lot. Then we don't have to configure static routes and it is not needed to configure <strong>wlan0</strong> with static values (IP address, gateway, DNS server, etc.).</p>
<h3>hostapd for bridge (Step 6)</h3>
<p>We have setup <em>hostapd</em> in Step 3. Now we only need to append <code>bridge=br0</code> to its configuration so that it will dynamically manage to add <strong>ap@wlan0</strong> to the bridge.</p>
<h3>wpa_supplicant for bridge (Step 7)</h3>
<p>When wpa_supplicant is started it also brings up interface <strong>wlan0</strong>. Every time it is managed, no matter if it started or stopped, it will stop <strong>ap@wlan0</strong> because it is not a real interface and depends directly on <strong>wlan0</strong>.</p>
<p>The ap interface can only start when <strong>wlan0</strong> "Gained carrier" and the link becomes ready <a href="https://github.com/systemd/systemd/issues/936" rel="nofollow noreferrer"><strong>(3)</strong></a>. This will happen some or more seconds after <em>wpa_supplicant</em> has started. There is a helper program <em>systemd-networkd-wait-online</em> that can do this synchronous. We use it with a timeout of 60 seconds. If your network connection takes longer than 60 seconds to get up,  then you should increase the timeout accordingly. With <code>journalctl -b -e</code> you can check if <code>Starting Bring up wifi interface ap@wlan0...</code> and <code>Started Bring up wifi interface ap@wlan0.</code> covers <code>wlan0: Gained carrier</code>. This is very important because otherwise, the bridge will not work correctly with undefined behavior. You can check the helpers options with <code>/lib/systemd/systemd-networkd-wait-online --help</code>.</p>
<p>After stopped wpa_supplicant (bring <strong>wlan0</strong> down) <strong>ap@wlan0</strong> must be brought up again so it can continue running for the access point.</p>
<h3>define static interfaces for bridge (Step 8)</h3>
<p>These files define the bridge. <strong>ap@wlan0</strong> will dynamically be added by <em>hostapd</em>. <strong>eth0</strong> and <strong>ap@wlan0</strong> are slaves of the bridge and don't need an IP address. The bridge <strong>br0</strong> itself also does not need an IP address but here it has a static IP address because we need it for the DHCP server bound to <strong>br0</strong> so the DHCP server is available on the subnet of the bridge ( interfaces eth0, ap@wlan0).</p>
<h3>Conclusion</h3>
<p><strong>Update</strong> 2020-07-22:<br />
<a href="https://raspberrypi.stackexchange.com/users/120864/bassline-soup">Bassline Soup</a> has made some <a href="https://raspberrypi.stackexchange.com/a/113521/79866">interesting tests</a> that may help to troubleshoot the setup.</p>
<hr />
<p>You are now able to start, stop and restart <em>hostapd</em> and <em>wpa_supplicant</em>.</p>
<p>You should see the access point, here <em>RPiNet</em>, in your mobile phone and should get an IP address to connect to the access point. You should also get an IP address from the same subnet if you connect a laptop with a cable to the ethernet port and you can ping the mobile phone.</p>
<p>With this setup you have the following dependencies with starting and stopping:</p>

```
 hostapd   │ wpa_supplicant      wpa_supplicant │  hostapd
───────────┼────────────────────────────────────┼──────────
 starting  │    starts              starting    │  starts
 stopping  │    stops               stopping    │   ----
restarting │   restarts            restarting   │  starts
```
<p>This is because of the strict order of starting (see section <em>General</em>). You cannot run <em>wpa_supplicant</em> without <em>hostapd</em> but you can run <em>hostapd</em> without <em>wpa_supplicant</em> by starting <em>hostapd</em> and then stop <em>wpa_supplicant</em>.</p>
<p>If communication stops for some reason (e.g. delay to small or something else) it is mostly enough to kick <strong>ap@wlan0</strong> with <code>/bin/ip link set ap@wlan0 up</code>.</p>
<br/>
<p><strong>references:</strong><br />
[1] <a href="https://raspberrypi.stackexchange.com/a/78788/79866">Howto migrate from networking to systemd-networkd with dynamic failover</a><br />
[2] man systemd.unit<br />
[3] <a href="https://github.com/systemd/systemd/issues/936" rel="nofollow noreferrer">systemd-networkd wireless bridging - need to wait for carrier</a><br />
[4] <a href="https://raspberrypi.stackexchange.com/a/97939/79866">Setup WiFi on Pi 3 B+</a></p>
