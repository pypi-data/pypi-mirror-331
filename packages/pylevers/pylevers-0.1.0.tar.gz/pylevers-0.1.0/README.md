# pylevers

A Python client for Levers.

## Installation
bash 
pip install pylevers

## Usage
python 
from pylevers import Client
client = Client('127.0.0.1', 8099) 
status, server_info = client.connect() 
print(status, server_info)

