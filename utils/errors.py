class ProxyError(Exception):
    pass

class ProxyConnectionError(ProxyError):
    pass

class ProxyConnectionClosed(ProxyError):
    pass

class PipeError(ProxyError):
    pass