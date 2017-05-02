# mbed Connector long poll client

## Setup

   1. `mkvirtualenv mbed_connector_long_poll`
   1. `pip install -r requirements.txt`
   2. Put your mbed connector app key in `$HOME/.netrc` like this:
    machine api.connector.mbed.com login [whatever] password [appkey]

## Run

    long_poll_connector_endpoint.py [myendpointpath]
