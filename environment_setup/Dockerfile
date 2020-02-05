FROM conda/miniconda3

LABEL org.label-schema.vendor = "Microsoft" \
    org.label-schema.url = "https://hub.docker.com/r/microsoft/mlopspython" \
    org.label-schema.vcs-url = "https://github.com/microsoft/MLOpsPython"

COPY diabetes_regression/ci_dependencies.yml /setup/
RUN conda update -n base -c defaults conda
RUN conda install python=3.7.5
RUN conda env create -f /setup/ci_dependencies.yml

# Activate environment
#SHELL ["conda", "run", "-n", "mlopspython_ci", "/bin/bash", "-c"]
# Alternate Way to activate Conda Env
ENV PATH /usr/local/envs/mlopspython_ci/bin:$PATH
RUN /bin/bash -c "source activate mlopspython_ci"

# Verify conda installation.
# This serves as workaround for https://github.com/conda/conda/issues/8537 (conda env create doesn't fail
# if pip installation fails, for example due to a wrong package version).
# The `az` command is not available if pip has not run (and installed azure-cli).
RUN az --version

ENTRYPOINT conda init bash
