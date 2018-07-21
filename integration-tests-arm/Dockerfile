# Systemd inside a Docker container, for CI only
ARG distro=stretch
FROM resin/rpi-raspbian:$distro

RUN apt-get update --yes

RUN apt-get install --yes curl git python3 python3-pip

# Kill all the things we don't need
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -exec rm \{} \;

RUN mkdir -p /etc/sudoers.d

RUN systemctl set-default multi-user.target

STOPSIGNAL SIGRTMIN+3

# Set up image to be useful out of the box for development & CI
ENV TLJH_BOOTSTRAP_DEV=yes
ENV TLJH_BOOTSTRAP_PIP_SPEC=/srv/src
ENV PATH=/opt/tljh/hub/bin:${PATH}

CMD ["/bin/bash", "-c", "exec /sbin/init --log-target=journal 3>&1"]
