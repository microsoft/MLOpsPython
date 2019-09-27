FROM conda/miniconda3

LABEL org.label-schema.vendor = "Microsoft" \
      org.label-schema.url = "https://hub.docker.com/r/microsoft/mlopspython" \
      org.label-schema.vcs-url = "https://github.com/microsoft/MLOpsPython"

       

COPY environment_setup/requirements.txt  /setup/
	
RUN apt-get update && apt-get install gcc -y && pip install --upgrade -r /setup/requirements.txt && \ 
    conda install -c r r-essentials
    # R --vanilla -e 'install.packages(c( "RPostgreSQL", \
    #                                     "DBI",         \
    #                                     "lubridate",   \
    #                                     "RSQLite",     \
    #                                     "magrittr",    \
    #                                     "zoo",         \
    #                                     "functional",  \
    #                                     "moments",     \
    #                                     "fpc",         \
    #                                     "RcppRoll",    \
    #                                     "cowplot",     \
    #                                     "tsne",        \
    #                                     "config",      \
    #                                     "factoextra",  \
    #                                     "NMF",         \
    #                                     "ggcorrplot",  \
    #                                     "umap"), repos="http://cran.r-project.org")'

CMD ["python"]