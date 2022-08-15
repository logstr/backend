FROM python:3.8.5

LABEL Author="Logstr Team"
LABEL E-mail="leslie.etubo@gmail.com"
LABEL version="0.0.1b"


WORKDIR /home/rq

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install rq

CMD ["rq worker -u redis://localhost:6379 high"]
# docker system prune (to free all used space)
# docker ps (to see all docker processes)
# docker stop [container_name] (to stop a particular container)
# docker run -d --name [sweet name for your container] -p 5000:5000 news_app (to run app in docker)
# docker attach [detached hash e.g a043d0f......]
# docker ps -a(to see running container)
# docker exec (to operate on a file in your docker container)
# docker run --name postgres -e POSTGRES_PASSWORD=Geronimo -d postgres
