"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import pandas as pd
import joblib
import sys
from typing import List
from util.model_helper import get_latest_model

model = None


def parse_args() -> List[str]:
    """
    The AML pipeline calls this file with a set of additional command
    line arguments whose names are not documented. As such using the
    ArgumentParser which necessitates that we supply the names of the
    arguments is risky should those undocumented names change. Hence
    we parse the arguments manually.

    :returns: List of model filters

    :raises: ValueError
    """
    model_name_param = [
        (sys.argv[idx], sys.argv[idx + 1])
        for idx, itm in enumerate(sys.argv)
        if itm == "--model_name"
    ]

    if len(model_name_param) == 0:
        raise ValueError(
            "Model name is required but no model name parameter was passed to the script"  # NOQA: E501
        )

    model_name = model_name_param[0][1]

    model_tag_name_param = [
        (sys.argv[idx], sys.argv[idx + 1])
        for idx, itm in enumerate(sys.argv)
        if itm == "--model_tag_name"
    ]
    model_tag_name = (
        None
        if len(model_tag_name_param) < 1
        or len(model_tag_name_param[0][1].strip()) == 0  # NOQA: E501
        else model_tag_name_param[0][1]
    )

    model_tag_value_param = [
        (sys.argv[idx], sys.argv[idx + 1])
        for idx, itm in enumerate(sys.argv)
        if itm == "--model_tag_value"
    ]
    model_tag_value = (
        None
        if len(model_tag_value_param) < 1
        or len(model_tag_name_param[0][1].strip()) == 0
        else model_tag_value_param[0][1]
    )

    return [model_name, model_tag_name, model_tag_value]


def init():
    """
    Initializer called once per node that runs the scoring job. Parse command
    line arguments and get the right model to use for scoring.
    """
    try:
        print("Initializing batch scoring script...")

        model_filter = parse_args()
        amlmodel = get_latest_model(
            model_filter[0], model_filter[1], model_filter[2]
        )  # NOQA: E501

        global model
        modelpath = amlmodel.get_model_path(model_name=model_filter[0])
        model = joblib.load(modelpath)
        print("Loaded model {}".format(model_filter[0]))
    except Exception as ex:
        print("Error: {}".format(ex))


def run(mini_batch: pd.DataFrame) -> pd.DataFrame:
    """
    The run method is called multiple times by the runtime. Each time
    a mini-batch consisting of a portion of the input data is passed
    in as a pandas DataFrame. The run method should return the scoring
    results as a List or a pandas DataFrame.

    :param mini_batch: Dataframe containing a portion of the scoring data

    :returns: array containing the scores.
    """

    try:
        result = None

        for _, sample in mini_batch.iterrows():
            # prediction
            pred = model.predict(sample.values.reshape(1, -1))
            result = (
                np.array(pred) if result is None else np.vstack((result, pred))
            )  # NOQA: E501

        return (
            []
            if result is None
            else mini_batch.join(pd.DataFrame(result, columns=["score"]))
        )

    except Exception as ex:
        print(ex)
