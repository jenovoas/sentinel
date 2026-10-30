FROM guacamole/guacamole:1.6.0

USER root
COPY certs/pinguinoseguro-ad-ldap-ca.crt /tmp/pinguinoseguro-ad-ldap-ca.crt
RUN keytool -importcert -noprompt -trustcacerts \
    -alias pinguinoseguro-ad-ldap-ca \
    -file /tmp/pinguinoseguro-ad-ldap-ca.crt \
    -keystore "${JAVA_HOME}/lib/security/cacerts" \
    -storepass changeit \
    && rm -f /tmp/pinguinoseguro-ad-ldap-ca.crt

USER guacamole
