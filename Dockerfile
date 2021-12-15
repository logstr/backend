FROM python:3.8.5

LABEL Author="Logstr Team"
LABEL E-mail="leslie.etubo@gmail.com, gastonnkh@gmail.com"
LABEL version="0.0.1b"

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP bevy.py
ENV FLASK_ENV development
ENV FLASK_DEBUG True
ENV FLASK_RUN_PORT 8000

WORKDIR /home/logstr

COPY ./requirements.txt /home/logstr

RUN pip install -r ./requirements.txt

COPY . /home/logstr


EXPOSE 5000

RUN chmod u+x ./boot.sh
ENTRYPOINT ["./boot.sh"]
# docker sytem prune (to free all used space)
# docker ps (to see all docker processes)
# docker stop [container_name] (to stop a particular container)
# docker run -d --name [sweet name for your container] -p 5000:5000 news_app (to run app in docker)
# docker attach [detached hash e.g a043d0f......]
# docker ps -a(to see running container)
# docker exec (to operate on a file in your docker container)

