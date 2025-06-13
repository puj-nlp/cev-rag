FROM docker.io/continuumio/anaconda3

RUN conda install jupyter -y --quiet

COPY ./run_jupyter.sh /bin/run_jupyter.sh
RUN chmod a+x /bin/run_jupyter.sh

COPY requirements.txt /tmp/pythonr1.txt
RUN pip install -r /tmp/pythonr1.txt

CMD ["/bin/run_jupyter.sh"]
