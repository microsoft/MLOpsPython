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

from azure.storage.blob import ContainerClient
from datetime import datetime, date, timezone
import argparse
import os
from utils.logger.observability import Observability

observability = Observability()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, default=None)
    parser.add_argument("--scoring_datastore", type=str, default=None)
    parser.add_argument("--score_container", type=str, default=None)
    parser.add_argument("--scoring_datastore_key", type=str, default=None)
    parser.add_argument("--scoring_output_filename", type=str, default=None)

    return parser.parse_args()


def copy_output(args):
    observability.log("Output : {}".format(args.output_path))

    accounturl = "https://{}.blob.core.windows.net".format(
        args.scoring_datastore
    )  # NOQA E501

    containerclient = ContainerClient(
        accounturl, args.score_container, args.scoring_datastore_key
    )

    destfolder = date.today().isoformat()
    filetime = (
        datetime.now(timezone.utc)
        .time()
        .isoformat("milliseconds")
        .replace(":", "_")
        .replace(".", "_")
    )  # noqa E501
    destfilenameparts = args.scoring_output_filename.split(".")
    destblobname = "{}/{}_{}.{}".format(
        destfolder, destfilenameparts[0], filetime, destfilenameparts[1]
    )

    destblobclient = containerclient.get_blob_client(destblobname)
    with open(
        os.path.join(args.output_path, "parallel_run_step.txt"), "rb"
    ) as scorefile:  # noqa E501
        destblobclient.upload_blob(scorefile, blob_type="BlockBlob")


if __name__ == "__main__":
    args = parse_args()
    if (
        args.scoring_datastore is None
        or args.scoring_datastore.strip() == ""
        or args.score_container is None
        or args.score_container.strip() == ""
        or args.scoring_datastore_key is None
        or args.scoring_datastore_key.strip() == ""
        or args.scoring_output_filename is None
        or args.scoring_output_filename.strip() == ""
        or args.output_path is None
        or args.output_path.strip() == ""
    ):
        observability.log("Missing parameters")
    else:
        copy_output(args)
