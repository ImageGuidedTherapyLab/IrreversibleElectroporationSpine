FROM petscbuild
MAINTAINER David Fuentes, fuentesdt@gmail.com
ARG USER_NAME="ire"

USER root
COPY c3d /usr/local/bin
RUN mkdir /data
RUN chmod 777 /data
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}
RUN git clone https://github.com/ImageGuidedTherapyLab/IrreversibleElectroporationSpine.git
WORKDIR /home/${USER_NAME}/IrreversibleElectroporationSpine/Code
RUN make ireSolver 
WORKDIR /data

ENTRYPOINT ["python", "/home/ire/IrreversibleElectroporationSpine/Code/ireSolver.py"]
