from xrpl.models.response import Response as XrplResponse


class CacheError(Exception):
    pass


class RpcFetchError(Exception):
    
    def __init__(self, message: str, response: XrplResponse | None = None):
        super().__init__(message)
        self.response = response

    @classmethod
    def new(cls, message: str, response: XrplResponse):
        if response.status == 'error' and response.result.get('error') == 'lgrIdxMalformed':
            return RpcLedgerRangeError(f"{message}: {response}", response)
        return cls(f"{message}: {response}", response)


class RpcLedgerRangeError(RpcFetchError):
    pass


class RpcSendError(Exception):
    pass
