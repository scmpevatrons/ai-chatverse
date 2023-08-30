FROM 'python:3.10.13-slim-bullseye'
LABEL org.opencontainers.image.authors="scm@pevatrons.net"
ARG CODE_HOME=/home/app/code/
ENV CODE_HOME=${CODE_HOME}
RUN mkdir -p ${CODE_HOME}
WORKDIR ${CODE_HOME}
COPY requirements.txt ${CODE_HOME}
RUN pip3 install -r requirements.txt
COPY . ${CODE_HOME}
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "🏠_Home.py"]

