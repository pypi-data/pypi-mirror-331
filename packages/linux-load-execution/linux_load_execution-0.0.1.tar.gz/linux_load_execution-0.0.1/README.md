# linux_load_execution

[![PyPI version](https://pypi.org/project/linux_load_execution/)]

## Overview

linux_load_execution is a Python package designed to:
Takes details like, lpar, ipaddress, script directory and script command as the input, and perform below activities

1. To call the zhmclient to activate the lpar, Sleep for 10 minutes
2. ssh to the ipaddress (Linux guest ip address)
3. download the script file to, local machine, from given source path
4. upload the dowloaded script file to the dir(/ffdc/u/eATS_automation) on the ssh session
5. invoke the script command (ex: sh make_loop.sh) on the ssh session
6. collect the output printed on the ssh session and print it


## Installation

You can install the package using pip:

```bash
pip install linux_load_execution
```
## config JSON format

```bash
config.json

{
    "host_name": "ip address of host",
    "hmcm_user_name": "user name of HMC",
    "hmcm_pwd": "password of HMC",
    "cpc": "cpc details",
    "lpar": "lpar details",
    "system_host": "ip address of host system",
    "userid": "user id",
    "user_pwd": "user password",
    "ssh_key_path": "SSH_KEY_PATH",
    "script_details": {
        "token": "",
        "name": "example.sh",
        "url": "path to script file",
        "exec_path": "path to execution",
        "local_path": "./"
    }
}
```
## Usage example

``` bash
main.py
*******
from activation import Activation


activation_obj = Activation(sys.argv[1])
activation_obj.entry_point()

```
## Running the Python code

``` bash

python main.py config.json

```

## Python package creation

[REFERENCE](https://packaging.python.org/en/latest/tutorials/packaging-projects//)