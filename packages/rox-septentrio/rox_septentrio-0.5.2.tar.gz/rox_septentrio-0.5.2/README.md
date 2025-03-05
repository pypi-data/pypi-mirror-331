# Septentrio GPS


**What it does:**

* Reads NMEA messages from the gps receiver (over serial or ip)
* parses them and calculates ENU coordinates
* publishes `latlon` and `enu` data as json to mqtt topics.

**mqtt messages**

```
topic: /gps/position
{"lat":51.45655803,"lon":6.08187908,"x":-13.354,"y":-67.59,"gps_qual":4,"time":"14:27:27.800000","ts":1726149158.437}

topic: /gps/direction
{"heading":152.22,"heading_stdev":0.084,"theta":-1.0859,"ts":1726149158.441}
```


## 1. Configure receiver

Install and configure gps receiver as described in [installation manual](docs/README.md)


## 2. Launch docker container

get docker image (use tag for version)

    registry.gitlab.com/roxautomation/components/septentrio-gps:latest

launch container with

    docker run \
    -e GPS_NODE_TYPE=ip \
    -e GPS_IP_HOST=<hostname> \
    registry.gitlab.com/roxautomation/components/septentrio-gps:latest


Set these environment variables to override default settings:

### MQTT
- **MQTT_HOST**: MQTT server host (default: `"localhost"`).
- **MQTT_PORT**: MQTT server port (default: `1883`).
- **MQTT_POSITION_TOPIC**: MQTT topic for GPS positions (default: `"/gps/position"`).
- **MQTT_DIRECTION_TOPIC**: MQTT topic for GPS directions (default: `"/gps/direction"`).

### GPS
- **GPS_NODE_TYPE**: "serial" or "ip" (default: `"serial"`).
- **GPS_SERIAL_PORT**: Serial port for GPS (default: `"/dev/gps_nmea"`).
- **GPS_SERIAL_BAUD**: Baud rate for GPS serial communication (default: `115200`).
- **GPS_IP_HOST** : ip server address (default `localhost`)
- **GPS_IP_PORT** : ip port (default `28000`)
- **GPS_REF**: gps reference point, provide lat,lon, example: `GPS_REF="51.123,6.456"`

## Precision
 - **DIGITS_POSITION** : meter position accuracy, defaults to 3
 - **DIGITS_LATLON** : digits latitude and longitude, defaults to 8
 - **DIGITS_ANGLE** : angle accuracy, defaults to 4


(note: configuration is defined in `config.py`)



## Development

There should be mqtt broker available on the host system. If not, there is a docker image for that:

    docker run -d --name mosquitto --restart unless-stopped -p 1883:1883 registry.gitlab.com/roxautomation/images/mosquitto:latest

* Open in VSCode devcontainer. Virtual com port is located at `/tty/tty_nmea_rx`
* Pre-recorded nmea stream can be sent to com port with `replay_data.py` in `integration/data` folder.
