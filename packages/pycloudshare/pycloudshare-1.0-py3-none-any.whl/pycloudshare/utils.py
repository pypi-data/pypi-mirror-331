import os
import logging

def load_api_vars():
    logging.debug('Loading API credentials')
    key_list = [
        'CLOUDSHARE_API_ID',
        'CLOUDSHARE_API_KEY',
        'CLOUDSHARE_API_HOSTNAME',
        'CLOUDSHARE_API_URL',
        'CLOUDSHARE_ACCELERATE_API_URL',
        'CLOUDSHARE_PROJECT_ID',
    ]
    keys = {key: os.environ.get(key, None) for key in key_list}
    if not all(keys.values()):
        logging.error('Missing API environment variables')
    else:
        logging.debug('API credentials loaded successfully')
    return keys
