# =======================================================================
# Our OpenShift 3.7/3.9 environments don't support the --chown flag.
# ---
# Docker Engine goes up to 1.13.1 (last release), 
# all newer releases are called  Docker CE or Docker EE starting at 
# version 17.03.0.
#
# Openshift 3.7 => docker engine 1.12
# Openshift 3.9 => docker engine 1.13
# =======================================================================

# Make some modifications to the python-s2i image to support
# dynamic creation of issuer services based on the container's
# deployment configuration.
FROM andrewwhitehead/von-image:py36-1.0rc1-debug-s2i 

USER root

# We don't need to collect any static files from the Permitify Django app during the s2i build
# and the application does not use a database.
ENV DISABLE_COLLECTSTATIC=true
ENV DISABLE_MIGRATE=true

# Create a wallet directory so we can set the permissions for any volumes mounted to it.
RUN mkdir -p $HOME/.indy_client/wallet

# Mount our issuer service initialization process in front of the s2i run script.
RUN mv ${STI_SCRIPTS_PATH}/run ${STI_SCRIPTS_PATH}/s2i_run
ADD ./docker/docker-entrypoint.sh ${STI_SCRIPTS_PATH}/run

RUN chmod -R ug+rwx $STI_SCRIPTS_PATH && \
    chmod -R ug+rw $HOME/.indy_client

ADD ./site_templates $HOME/site_templates

USER 1001