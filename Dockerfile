FROM 'python:3.10.13-bookworm'

# Install Debian software needed by MetaGPT and clean up in one RUN command to reduce image size
RUN apt remove gcc -y &&\
    apt update &&\
    apt install -y git gcc-11 chromium fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 build-essential cmake npm --no-install-recommends &&\
    apt clean && rm -rf /var/lib/apt/lists/*
ENV UNAME_M=arm64 UNAME_p=arm LLAMA_NO_METAL=1
# Install Mermaid CLI globally
ENV CHROME_BIN="/usr/bin/chromium"
RUN npm install -g @mermaid-js/mermaid-cli &&\
    npm cache clean --force
LABEL org.opencontainers.image.authors="scm@pevatrons.net"
ARG CODE_HOME=/home/app/code/
ENV CODE_HOME=${CODE_HOME}
RUN mkdir -p ${CODE_HOME}
RUN pip3 install --upgrade pip
WORKDIR ${CODE_HOME}
COPY requirements.txt ${CODE_HOME}
RUN pip3 install -r requirements.txt
COPY assets ${CODE_HOME}/assets
COPY backend ${CODE_HOME}/backend
COPY configs ${CODE_HOME}/configs
COPY config ${CODE_HOME}/config
COPY handlers ${CODE_HOME}/handlers
COPY schema ${CODE_HOME}/schema
ENV PUPPETEER_CONFIG="${CODE_HOME}/configs/puppeteer-config.json"\
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
COPY models ${CODE_HOME}/models
COPY conversations ${CODE_HOME}/conversations
RUN mkdir -p ${CODE_HOME}/artifacts
COPY pages ${CODE_HOME}/pages
COPY ui_elements ${CODE_HOME}/ui_elements
COPY utils ${CODE_HOME}/utils
COPY .streamlit ${CODE_HOME}/.streamlit
COPY *.py ${CODE_HOME}/
RUN touch .gitignore
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "Multi_Agent_Collab.py"]

