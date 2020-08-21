# Fakeroo

This repo contains a simple Python script that can be used to generate test data.

## Usage

The usage is fairly simple, to install the dependencies and use one of the supplied examples:

```
$ pip3 install -r requirements.txt
$ python3 fakeroo.py -v examples/user_account_data.yaml  
```

Run the script without any parameters to get the command-line help:

```
$ python3 fakeroo.py
usage: fakeroo.py [-h] [-f FILENAME] [-n ROWS] [-q] [-v]
                  yaml_files [yaml_files ...]
fakeroo.py: error: the following arguments are required: yaml_files
```