
class Context(object):
    def __init__(self, region_id, credentials, extra_parameters=None):
        self.region_id = region_id
        self.credentials = credentials
        self.extra_parameters = extra_parameters
