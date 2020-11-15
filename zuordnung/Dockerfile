# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

COPY docker_entrypoint.sh /

RUN chmod a+x /docker_entrypoint.sh

ENTRYPOINT ["/docker_entrypoint.sh"]
