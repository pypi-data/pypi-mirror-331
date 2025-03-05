# Installation

**NOTE:** installation scripts are in `install` folder.


1. run `install_gps.sh`. This will install udev rules.
2. run `install_ntrip.sh` to install ntrip client. **TODO** : add service
3. restart the system, plug in gps. Gps should now be accessible:
   -  `/dev/gps_nmea` : endpoint for nmea data
   -  `/dev/gps_rtcm` : endpoint for sending corrections
   -  `192.168.3.1` : web ui


## Forward web interface

### Using `socat` (manual)

The web interface of Septentrio can be forwarded by `socat`

`socat tcp-listen:9000,reuseaddr,fork tcp:192.168.3.1:80`


### Using systemd (automatic)

install service using

`install/install_forward_service.sh`


### Using `ssh`

alternatively `ssh` can be used for port forwarding.
when working on a remote device
connect with ssh with:

`ssh -L 8080:192.168.3.1:80 <device_ip>`

This wil forward webui to `localhost:8080`

Tip: you can use `.ssh/config` to save configuration like this:

```
Host reterm01
  HostName reterm01.local
  User pi
  LocalForward 8080 192.168.3.1:80

```


## GPS receiver config
From the default configuration of the septentrio receiver, change the following settings:



1. Create new NMEA stream (one or both)
      -  (NMEA/SBF Out) --> (New NMEA stream) --> (USB port) --> (USB1)
      -  **preferred**: IP Server (port 28000, TCP send only)
2. Interval: 200msec
3. Enable messages: GGA+VTG+HRP+HDT

![image.png](img/gps-message-config.png)


[![Watch the video](https://img.youtube.com/vi/ArtePkC58-o/0.jpg)](https://www.youtube.com/watch?v=ArtePkC58-o)


And save the seting to the "BOOT" settings


## References

* [webinar ROSaic](https://youtu.be/PFSxcOPnfjQ)
* [github code](https://github.com/septentrio-gnss/septentrio_gnss_driver)
* [simple config](https://msadowski.github.io/rtk-plug-n-play-with-septentrio/)
* [mosaic docs](https://www.septentrio.com/en/products/gnss-receivers/gnss-modules/mosaic-h)
* [Rpi & mosaic (TUD)](http://gnss1.tudelft.nl/pub/varia/Septentrio_mosaic-go_raspberry_pi_zero_w.pdf)
* [Septentrio docs Mosaic-H](https://www.septentrio.com/en/products/gps/gnss-receiver-modules/mosaic-h#resources)
