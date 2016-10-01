#
#  Dockerfile for XSS Hunter
#  v0.1 - By Moloch
#
FROM xsshunter_python:latest
MAINTAINER moloch

#
# > Copy code over
#
RUN mkdir /opt/xsshunter
ADD . /opt/xsshunter


#
# > Entrypoint & Volumes
#
VOLUME ["/opt/xsshunter/logs"]
ENTRYPOINT ["/opt/xsshunter/apiserver.py"]
