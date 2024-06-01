FROM python:3.11-slim
WORKDIR /birdnet
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg
COPY src ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-u", "/birdnet/main.py"]