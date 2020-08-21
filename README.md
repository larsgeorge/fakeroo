# Fakeroo

This repo contains a simple Python script that can be used to generate test data.
It is based on the [Faker](https://faker.readthedocs.io/en/stable/index.html) Python library, but extends it to generate not on CSV/DSV files, but also other ones. 
In addition, it can correlate fields in a row, so that they *match* better.
For instance, the geo location follows the country code within a row.

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