FROM ubuntu:xenial
MAINTAINER David Fuentes, fuentesdt@gmail.com

# setup dependencies 
RUN apt-get update

# Install compiler tools.
RUN apt-get install -y make gcc gfortran wget python pkg-config sudo

# PETSc requires BLAS, LAPACK and MPI.
#RUN apt-get install -y libblas-dev liblapack-dev libopenmpi-dev openmpi-bin openssh-client
RUN apt-get install -y libopenmpi-dev openmpi-bin openssh-client

# setup non root user
ARG USER_NAME="ire"
RUN adduser --disabled-password --gecos '' --shell /bin/bash ${USER_NAME}
RUN usermod -aG sudo ${USER_NAME}
USER ${USER_NAME}
ENV HOME=/home/${USER_NAME}
RUN chmod 777 /home/${USER_NAME}
WORKDIR /home/${USER_NAME}

# Select the latest stable releases of PETSc and SLEPc.
#
# http://www.mcs.anl.gov/petsc/download/
# http://www.grycap.upv.es/slepc/download/
ENV PETSC_VERSION 3.5.4


# Download and extract PETSc.
RUN wget --no-verbose http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-$PETSC_VERSION.tar.gz
RUN gunzip -c petsc-lite-$PETSC_VERSION.tar.gz | tar -xof -

ENV PETSC_DIR /home/${USER_NAME}/petsc-$PETSC_VERSION
ENV PETSC_ARCH arch-linux2-c-debug

WORKDIR $PETSC_DIR

# Configure and build PETSc.
RUN ./config/configure.py --with-shared-libraries --with-clanguage=c++ --CFLAGS='-g -O0' --CXXFLAGS='-g -O0' --download-ctetgen  --download-triangle --with-debugging=yes  --download-fblaslapack   --download-netcdf  --download-exodusii --download-hdf5  --with-c2html=0
RUN make all
# RUN make test
   
# Add the newly compiled libraries to the environment.
ENV LD_LIBRARY_PATH $PETSC_DIR/$PETSC_ARCH/lib
ENV PKG_CONFIG_PATH $PETSC_DIR/$PETSC_ARCH/lib/pkgconfig
