FROM python:3-slim

ARG USERNAME=dev
ARG UID=1000
ARG GID=1000
ARG IMG_NAME=septentrio_gps

# Set environment variables to ensure scripts in non-interactive mode don't stop for user input
ENV DEBIAN_FRONTEND=noninteractive

# Create the user
RUN groupadd --gid $GID $USERNAME \
    && useradd --uid $UID --gid $GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# dialout group
RUN usermod -a -G dialout $USERNAME

# install packages
RUN apt-get install -y \
    locales \
    tree \
    git \
    make \
    iputils-ping \
    socat \
    graphviz \
    picocom

# cleanup
RUN rm -rf /var/lib/apt/lists/*

# set locale
RUN export LC_ALL=en_US.UTF-8
RUN export LANG=en_US.UTF-8
RUN locale-gen en_US.UTF-8

RUN pip install pre-commit

# install package requirements
WORKDIR /root
COPY pyproject.toml pyproject.toml

# install dev requirements
COPY requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt

# create mount point for virtual ports
RUN mkdir -p /tty
RUN chown -R ${USERNAME} /tty

# copy entrypoint
COPY .devcontainer/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#-----------------DEV user-----------------

USER ${USERNAME}
RUN echo 'export PS1="🐳  \[\033[1;36m\]'"${IMG_NAME}"' \[\e[33m\]\W\[\e[m\] \[\033[1;36m\]# \[\033[0m\]"' >> ~/.bashrc

# add local bin to path
RUN echo "export PATH=\$PATH:/home/${USERNAME}/.local/bin" >> ~/.bashrc
ENV PATH="${PATH}:/home/${USERNAME}/.local/bin"


WORKDIR /home/${USERNAME}

# setup folders for saving vscode extensions
# https://code.visualstudio.com/remote/advancedcontainers/avoid-extension-reinstalls
RUN mkdir -p /home/$USERNAME/.vscode-server/extensions \
    && chown -R $USERNAME \
    /home/$USERNAME/.vscode-server



# build timestamp
USER root
RUN echo harvy-tools >> /build_date.txt && \
    date >> /build_date.txt

USER ${USERNAME}
WORKDIR /home/${USERNAME}

CMD [ "sleep", "infinity" ]
