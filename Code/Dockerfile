FROM ubuntu:xenial
MAINTAINER David Fuentes, fuentesdt@gmail.com

# setup dependencies 
RUN apt-get update

# Install compiler tools.
RUN apt-get install -y make gcc gfortran wget python pkg-config sudo

# PETSc requires BLAS, LAPACK and MPI.
RUN apt-get install -y libblas-dev liblapack-dev libopenmpi-dev openmpi-bin openssh-client

# dependencies 
RUN apt-get install -y libnetcdf-dev libhdf5-serial-dev libexodusii-dev libexodusii5

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
WORKDIR /opt
RUN wget --no-verbose http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-$PETSC_VERSION.tar.gz
RUN gunzip -c petsc-lite-$PETSC_VERSION.tar.gz | tar -xof -

ENV PETSC_DIR /opt/petsc-$PETSC_VERSION
ENV PETSC_ARCH arch-linux2-c-debug

WORKDIR $PETSC_DIR
## 
## # Configure and build PETSc.
## RUN ./configure
## #  --with-mpi=0 \
## #  --with-debugging=0 \
## #  --with-threadcomm --with-pthreadclasses \
## #  --download-superlu \
## #  --with-64-bit-indices
## RUN make all
## RUN make test
## 
## 
## 
## # Add the newly compiled libraries to the environment.
## ENV LD_LIBRARY_PATH $PETSC_DIR/$PETSC_ARCH/lib:$SLEPC_DIR/$PETSC_ARCH/lib
## ENV PKG_CONFIG_PATH $PETSC_DIR/$PETSC_ARCH/lib/pkgconfig:$SLEPC_DIR/$PETSC_ARCH/lib/pkgconfig
## 
## 
