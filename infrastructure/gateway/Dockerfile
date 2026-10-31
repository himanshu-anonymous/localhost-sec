FROM haproxy:2.8-alpine

USER root
RUN mkdir -p /etc/haproxy/certs /etc/haproxy/acl /var/run && \
    touch /etc/haproxy/acl/blocked_ips.lst && \
    chmod -R 777 /var/run /etc/haproxy/acl

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY acl/blocked_ips.lst /etc/haproxy/acl/blocked_ips.lst

EXPOSE 8088 8443
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]

