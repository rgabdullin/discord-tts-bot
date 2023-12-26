FROM ubuntu:22.04

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && apt-get install -y python3-dev python3-pip ffmpeg
RUN pip3 install -U pip wheel && pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /app
ADD tts_bot.py /app/tts_bot.py
ENTRYPOINT [ "python3" ]
CMD [ "tts_bot.py" ]
