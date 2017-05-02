#!/usr/bin/env python
import sys
import logging
import urllib2
import json
from netrc import netrc
from threading import Thread
from Queue import Queue, Empty
from base64 import b64decode
from urlparse import urlsplit

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

BASE_URL = "https://api.connector.mbed.com"


def get_opener(app_key):
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'Bearer %s' % app_key)]
    return opener


def long_poll(app_key):
    opener = get_opener(app_key)
    opener.addheaders += [('connection', 'keep-alive')]

    response_found = False
    async_id = None
    while not response_found:
        logger.debug("async_id: %r", async_id)
        logger.debug("polling")
        resp = opener.open(BASE_URL + "/v2/notification/pull")
        data = json.load(resp)
        logger.debug("got long poll response: %r", data)
        async_responses = data.get('async-responses', [])
        try:
            async_id = ASYNC_ID_QUEUE.get(block=False)
        except Empty:
            pass
        if async_id is not None:
            for async_response in async_responses:
                if async_response['id'] == async_id:
                    value = b64decode(async_response['payload'])
                    ASYNC_RESPONSE_QUEUE.put(value)
                    response_found = True
                    break


def main(argv=None):
    global ASYNC_ID_QUEUE
    global ASYNC_RESPONSE_QUEUE
    if argv is None:
        argv = sys.argv
    logging.basicConfig()
    endpoint = argv[1]
    url_parts = urlsplit(BASE_URL)
    _, _, app_key = netrc().authenticators(url_parts.netloc)
    
    ASYNC_ID_QUEUE = Queue()
    ASYNC_RESPONSE_QUEUE = Queue()

    opener = get_opener(app_key)
    long_poll_thread = Thread(target=long_poll, args=(app_key,))
    long_poll_thread.start()

    logger.debug("getting endpoint")
    resp = opener.open(BASE_URL + "/v2/endpoints/%s" % endpoint)
    data = json.load(resp)
    logger.debug("get resp: %r", data)
    async_id = data['async-response-id']

    ASYNC_ID_QUEUE.put(async_id)
    async_response = ASYNC_RESPONSE_QUEUE.get()
    long_poll_thread.join()
    print async_response


if __name__ == '__main__':
    sys.exit(main())
