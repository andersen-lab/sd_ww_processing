FROM condaforge/miniforge3:25.3.1-0

RUN apt update &&\
apt install -yy parallel rename git vim

RUN mamba create --name freyja python=3.11 &&\
conda config --add channels bioconda &&\
conda config --add channels conda-forge

RUN mamba run -n freyja mamba install -n freyja freyja=2.0.0  -y

COPY . /data
WORKDIR /data

RUN chmod +x ./demix_parallel_ubuntu.sh
RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
