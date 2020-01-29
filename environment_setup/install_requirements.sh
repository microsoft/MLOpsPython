#!/bin/bash

# Copyright (C) Microsoft Corporation. All rights reserved.​
#  ​
# Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
# royalty-free right to use, copy, and modify the software code provided by us
# ('Software Code'). You may not sublicense the Software Code or any use of it
# (except to your affiliates and to vendors to perform work on your behalf)
# through distribution, network access, service agreement, lease, rental, or
# otherwise. This license does not purport to express any claim of ownership over
# data you may have shared with Microsoft in the creation of the Software Code.
# Unless applicable law gives you more rights, Microsoft reserves all other
# rights not expressly granted herein, whether by implication, estoppel or
# otherwise. ​
#  ​
# THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

set -eux
pip install conda-merge==0.1.5
conda-merge environment_setup/ci_environment.yml diabetes_regression/scoring/scoring_dependencies.yml diabetes_regression/training/training_dependencies.yml > /tmp/conda_merged.yml
conda env create -f /tmp/conda_merged.yml
