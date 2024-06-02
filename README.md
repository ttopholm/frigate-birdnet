# Frigate-Birdnet
This repo contains a docker image for providing the names of the birds that Frigate picks up

# Installation

To use the docker images, you can run it with the following code:
```
docker run ghcr.io/ttopholm/frigate-birdnet:latest
```
## Environment Variables
| Variable      | Description | Mandatory | Default Value |
| ----------- | ----------- | ----------- | ----------- |
| mqtt-broker      | Mqtt host       | X ||
| mqtt-port    | Mqtt port        | | 1883 |
| longitude | Longitude of the place where cameras are located | X ||
| latitude  | Latitude of the place where cameras are located | X ||
| mqtt_reconnect_interval   | reconnect interval for reconnecting to mqtt server is connection was lost (in seconds)        | | 5 |
| subscribe_topic    | topic for subscribing to Frigate events        | | frigate/+/audio/bird |
| publish-topic   | The topic where bird data is published to      | | birdnet/bird |
| max_audio_duration    | Max left of recording from Frigate (in seconds)       | | 60 |
| max_analyze_workers   | Max workers for the analyzer      | | 3 |
| min_confidence    | Minimum confidence for the result        | | 0.25 |

# Output format
```
{
    "image_url":"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/242173971/900",
    "common_name":"Common wood pigeon",
    "scientific_name":"Columba palumbus",
    "start_time":1717265299.484562,
    "end_time":1717265302.484562,
    "species_code":"cowpig1"
    "camera": "Backyard"
}
```

image_url and species_code will be per default empty, unless you add the ebird.org taxonomy file, [see here](#ebird-integration). By using the integration, you can also get the common_name translated into your local language

# Ebird integration
If you want the common name, species code and the image url, you need provide a ebird taxanomy file with the image included. Per default the ebird.org api doesn't provide the image, but by using the ebird_generate.py it can generate the file.

If you want to use the file, you will also need to add a volume with the <code>ebird_taxonomy.json</code> file in.

```
docker run -v ./labels:/birdnet/labels ghcr.io/ttopholm/frigate-birdnet:latest
```

## Installation of the ebird taxanomy generation tool

To use the tool, you need to install the dependencies in requirements-ebird.txt like this
```
pip install -r requirements-ebird.txt
```

## Obtain API key for ebird.org
Go to https://secure.birds.cornell.edu/cassso/login and create an user and obtain the api token.

## Run the generation tool
To run the generation tool, run the follow:
```
python ebird_generate.py --ebird-api-token=[api token from ebird] --country=[country you are located in] --locale=[Your locale]
```
<code>country</code> can be either your ISO 2 letter country, or it can also include sub region, fx. DK-85 (Which is Denmark, Zealand)

<code>locale</code> is you locale, fx. da


# Home assistant
If you want it in Home Assistant as an image use the follow MQTT Image code:

```
mqtt
  image:
    - name: birdnet
      unique_id: birdnet
      url_topic: "birdnet/bird"
      url_template: "{{ value_json.image_url }}"
      json_attributes_topic: "birdnet/bird"
      json_attributes_template: >
        { "name": {{value_json.common_name}} }
```