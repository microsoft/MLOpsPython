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
import subprocess


def az_login(sp_user: str, sp_password: str, sp_tenant_id: str):
    """
    Uses the provided service principal credentials to log into the azure cli.
    This should always be the first step in executing az cli commands.
    """
    cmd = "az login --service-principal --username {} --password {} --tenant {}"
    out, err = run_cmd(cmd.format(sp_user, sp_password, sp_tenant_id))
    return out, err


def run_cmd(cmd: str):
    """
    Runs an arbitrary command line command.  Works for Linux or Windows.
    Returns a tuple of output and error.
    """
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True
    )
    output, error = proc.communicate()
    if proc.returncode != 0:
        print("Following command execution failed: {}".format(cmd))
        raise Exception("Operation Failed. Look at console logs for error info")
    return output, error


def az_account_set(subscription_id: str):
    """
    Sets the correct azure subscription.
    This should always be run after the az_login.
    """
    cmd = "az account set  -s {}"
    out, err = run_cmd(cmd.format(subscription_id))
    return out, err


def az_acr_create(resource_group: str, acr_name: str):
    cmd = "az acr create --resource-group {} --name {} --sku Basic"
    out, err = run_cmd(cmd.format(resource_group, acr_name))
    return out, err


def az_acr_login(acr_name: str):
    cmd = "az acr login --name {}"
    out, err = run_cmd(cmd.format(acr_name))
    return out, err
