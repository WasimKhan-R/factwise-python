class BadRequest(Exception):
    pass

class NotFound(Exception):
    pass

class Conflict(Exception):
    pass
    # status_code = 409
    # default_detail = 'Conflict error'
    # default_code = 'conflict'
