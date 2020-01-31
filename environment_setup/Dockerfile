FROM conda/miniconda3

LABEL org.label-schema.vendor = "Microsoft" \
      org.label-schema.url = "https://hub.docker.com/r/microsoft/mlopspython" \
      org.label-schema.vcs-url = "https://github.com/microsoft/MLOpsPython"

COPY diabetes_regression/ci_dependencies.yml /setup/

RUN conda env create -f /setup/ci_dependencies.yml

# activate environment
ENV PATH /usr/local/envs/mlopspython_ci/bin:$PATH
RUN /bin/bash -c "source activate mlopspython_ci"

# Install Azure CLI ML extension.
# This also serves as workaround for https://github.com/conda/conda/issues/8537 (conda env create doesn't fail
# if pip installation fails, for example due to different version specs in the various environment files).
# The `az` command is not available if pip has not installed azure-cli.
RUN az extension add -n azure-cli-ml
