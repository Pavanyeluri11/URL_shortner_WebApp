import validators

def valid_url(url):
    return validators.url(url) is True