from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from ffmpeg.asyncio import FFmpeg
import aiohttp
from os import remove, environ
import aiomqtt
import models.frigate as frigate
import models.birdnet as birdnet
import models.ebird as ebird
import models.result as result
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os, sys
from paho.mqtt.publish import single as publish
from environs import Env

env = Env()
env.read_env()

# variables required
mqtt_broker = env.str("mqtt-broker")
longitude = env.float("longitude")
latitude = env.float("latitude")
frigate_url = env.str("frigate-host")

#optional
mqtt_port = env.int("mqtt-port", 1883)
mqtt_reconnect_interval = env.int("mqtt-reconnect-interval", 5)
subscribe_topic = env.str("subcribe-topic", "frigate/+/audio/bird")
publish_topic = env.str("publish-topic", "birdnet/bird") 
max_audio_duration = env.int("max-audio-duration", 60000)
max_analyze_workers = env.int('max-analyze-workers', 3)
min_confidence = env.float("min-confidence", 0.25)


def load_ebird_taxonomy():
    if os.path.exists("./labels/ebird_taxonomy.json"):
        with open("./labels/ebird_taxonomy.json", "r") as f:
            return ebird.Birds.model_validate_json(f.read())        

    return None


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

async def fetch_event(camera: str) -> frigate.Events:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{frigate_url}/api/events', params={
                    'labels': 'bird',
                    'cameras': camera,
                    'in_progress': 0,
                    'has_clip': 1,
                    'limit': 1
                }) as r:
                if r.status == 200:
                    return frigate.Events.model_validate_json(await r.text())
    except aiohttp.ClientConnectorError as e:
        print('no connection to Frigate http api')
    
    return False

async def extract_audio(event_id):
    try:
        video_url = f'{frigate_url}/api/events/{event_id}/clip.mp4'
        audio_filename = f'{event_id}.mp3'
        ffmpeg = (
            FFmpeg()
            .input(video_url)
            .output(audio_filename, 
                acodec='mp3'
            )
        )    
        await ffmpeg.execute()
        return True
    except Exception:
        print('ffmpeg failed')
        return False

def analyze_event(client: aiomqtt.Client, event: frigate.Event) -> None:
    audio_filename = f'{event.id}.mp3'
    
    try:
        with HiddenPrints():
            recording = Recording(
                analyzer,   
                audio_filename,
                lat=latitude,
                lon=longitude,
                date=datetime.now(),
                min_conf=min_confidence,
            )
            recording.analyze()

        birds = birdnet.Birds.model_validate(recording.detections)
        for bird in birds:
            bird_result = result.Bird.model_validate({
                'image_url': None,
                'species_code': None,
                'common_name': bird.common_name,
                'scientific_name': bird.scientific_name,
                'start_time': event.start_time + bird.start_time,
                'end_time': event.start_time + bird.end_time
            }) 
            if ebirds:
                for ebird in ebirds:
                    if bird.scientific_name == ebird.sciName:
                       bird_result.image_url = ebird.image
                       bird_result.species_code = ebird.speciesCode
                       bird_result.common_name = ebird.comName

            publish(publish_topic, bird_result.model_dump_json(), hostname=mqtt_broker)

        
        
        remove(audio_filename)

    except Exception as e:
        print(e)    

async def message_handler(client, msg):
    payload = msg.payload.decode()
    camera = msg.topic.value.split("/")[1]
    if payload == 'OFF':
            events = await fetch_event(camera)
            if events:
                event = events[0]
                event_id = event.id
                if event.duration < max_audio_duration:
                    if await extract_audio(event_id):
                        tpe.submit(analyze_event, client, event)

async def main():
    while True:
        try:
            async with aiomqtt.Client(mqtt_broker) as client:
                await client.subscribe(subscribe_topic)   
                async for message in client.messages:
                    await message_handler(client, message)
        except aiomqtt.MqttError:
            print(f"Connection lost; Reconnecting in {mqtt_reconnect_interval} seconds ...")
            await asyncio.sleep(mqtt_reconnect_interval)


if __name__ == '__main__':
    analyzer = Analyzer()
    ebirds = load_ebird_taxonomy()
    tpe = ThreadPoolExecutor(max_workers=max_analyze_workers)
    asyncio.run(main())