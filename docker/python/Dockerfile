####################################
#
#  Dockerfile for Tornado App Template Python
#  v0.1 - By Moloch
FROM python:2.7.11
MAINTAINER moloch


#
# > Update/Install Packages
#
RUN apt-get update -y && apt-get install -y build-essential
RUN pip install --upgrade pip
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt


#
# > Cleanup
#
RUN rm -f /tmp/requirements.txt
RUN apt-get purge -y build-essential && apt-get autoremove -y && apt-get clean -y
