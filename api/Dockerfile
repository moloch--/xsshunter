#
#  Dockerfile for XSS Hunter
#

FROM xsshunter_python:latest
MAINTAINER moloch
MAINTAINER mandatory

#
# > Copy code over
#
RUN mkdir /opt/xsshunter
ADD . /opt/xsshunter

#
# > Entrypoint & Volumes
#
ENTRYPOINT ["/opt/xsshunter/xsshunter.py"]
