FROM conda/miniconda3

LABEL org.label-schema.vendor = "Microsoft" \
      org.label-schema.url = "https://hub.docker.com/r/microsoft/mlopspython" \
      org.label-schema.vcs-url = "https://github.com/microsoft/MLOpsPython"

       

COPY environment_setup/requirements.txt  /setup/

COPY environment_setup/python.sh /usr/local/sbin/python.sh
RUN rm /usr/local/bin/python && ln -s /usr/local/sbin/python.sh /usr/local/bin/python

	
RUN apt-get update && apt-get install gcc -y && pip install --upgrade -r /setup/requirements.txt   

CMD ["python"]