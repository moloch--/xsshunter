####################################
#
#  Dockerfile for Tornado App Template Python
#  v0.1 - By Moloch
FROM python:2.7.11
MAINTAINER moloch


#
# > Fix Apt's broke ass
# https://github.com/docker-library/buildpack-deps/issues/40
#
RUN echo \
   'deb ftp://ftp.us.debian.org/debian/ jessie main\n \
    deb ftp://ftp.us.debian.org/debian/ jessie-updates main\n \
    deb http://security.debian.org jessie/updates main\n' \
    > /etc/apt/sources.list



#
# > Update/Install Packages
#
RUN apt-get update --fix-missing && apt-get install -y build-essential
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt


#
# > Cleanup
#
RUN rm -f /tmp/requirements.txt
RUN apt-get purge -y build-essential \
  && apt-get autoremove -y \
  && apt-get clean -y
