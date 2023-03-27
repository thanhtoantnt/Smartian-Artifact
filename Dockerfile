FROM ubuntu:22.04

RUN apt -y update
RUN apt -y install build-essential
RUN apt -y install cmake
RUN apt -y install git
RUN apt -y install curl
RUN apt -y install python3
RUN apt -y install python3-pip
RUN pip3 install solc-select
RUN solc-select install 0.4.16
RUN cp ~/.solc-select/artifacts/solc-0.4.16/solc-0.4.16 /bin/

RUN mkdir /home/test
RUN mkdir /home/test/tools/
RUN mkdir /home/test/tools/sFuzz
WORKDIR /home/test/tools/sFuzz
RUN git clone --recursive https://github.com/thanhtoantnt/sFuzz.git
WORKDIR sFuzz
RUN git pull
RUN ./scripts/install_deps.sh
RUN mkdir build
WORKDIR build
RUN cmake ../
WORKDIR fuzzer
RUN cp ../../assets . -r
RUN make
RUN mkdir output
RUN mkdir contracts

RUN cp /home/test/tools/sFuzz/sFuzz/build/fuzzer/fuzzer /home/test/tools/sFuzz/fuzzer

RUN pip install lark --upgrade
RUN pip install node-semver
RUN pip install semantic-version

RUN apt install -y libsqlite3-0 libsqlite3-dev
RUN apt install -y apt-utils
RUN apt install -y locales
RUN apt install -y python3-setuptools
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:ethereum/ethereum
RUN apt update
RUN apt install -y solc libssl-dev pandoc wget

WORKDIR /home/test/tools/mythril
RUN python3 -m pip install wheel
RUN git clone https://github.com/ConsenSys/mythril.git
WORKDIR /home/test/tools/mythril/mythril
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Add scripts for each tool
COPY ./docker-setup/tool-scripts/ /home/test/scripts

### Prepare benchmarks
COPY ./benchmarks /home/test/benchmarks

ENTRYPOINT [ "/bin/bash" ]