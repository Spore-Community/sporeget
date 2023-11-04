#Building wget-lua (https://github.com/ArchiveTeam/wget-lua)
FROM debian:bullseye-slim as wget_build
ARG TLSTYPE=openssl
ENV LC_ALL=C
RUN set -eux \
    && case "${TLSTYPE}" in openssl) SSLPKG=libssl-dev;; gnutls) SSLPKG=gnutls-dev;; *) echo "Unknown TLSTYPE ${TLSTYPE}"; exit 1;; esac \
    && DEBIAN_FRONTEND=noninteractive DEBIAN_PRIORITY=critical apt-get -qqy --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold -o Dpkg::Options::=--force-unsafe-io update \
    && DEBIAN_FRONTEND=noninteractive DEBIAN_PRIORITY=critical apt-get -qqy --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold -o Dpkg::Options::=--force-unsafe-io install "${SSLPKG}" build-essential git bzip2 bash rsync gcc zlib1g-dev autoconf autoconf-archive flex make automake gettext libidn11 autopoint texinfo gperf ca-certificates wget pkg-config libpsl-dev libidn2-dev libluajit-5.1-dev libgpgme-dev libpcre2-dev
RUN cd /tmp \
    && wget https://github.com/facebook/zstd/releases/download/v1.4.4/zstd-1.4.4.tar.gz \
    && tar xf zstd-1.4.4.tar.gz \
    && cd zstd-1.4.4 \
    && make \
    && make install
RUN ldconfig
RUN git clone --recurse-submodules -b v1.21.3-at https://github.com/ArchiveTeam/wget-lua /tmp/wget \
    && cd /tmp/wget \
    && ./bootstrap \
    && ./configure --with-ssl="${TLSTYPE}" --disable-nls \
    && make -j $(nproc) \
    && mkdir -p ~/bin/ && cp ./src/wget ~/bin/wget-lua

#Preparing sporeget image
FROM python:3.9-slim-bullseye

COPY --from=wget_build /tmp/wget/src/wget /bin/wget-lua
COPY --from=wget_build /usr/local/lib /usr/local/lib
COPY --from=wget_build /usr/lib /usr/lib

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

#Creating an alias for /app/sporeget_wget.sh & printing help
RUN echo '#!/bin/bash\nbash /app/sporeget_wget.sh "$@"' > /usr/bin/sporeget \
    && chmod +x /usr/bin/sporeget
CMD bash sporeget_wget.sh && /bin/sh
