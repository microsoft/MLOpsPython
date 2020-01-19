FROM conda/miniconda3

RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gcc

# Install dotnet runtime used to generate code coverage report
RUN curl -O https://packages.microsoft.com/config/ubuntu/19.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update && apt-get install -y dotnet-runtime-3.1

# Uncomment to run R
# RUN conda install -c r r-essentials

# Install Python modules
COPY requirements.txt  /setup/
RUN pip install --upgrade -r /setup/requirements.txt
