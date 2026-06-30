from __future__ import annotations


class ObsdnError(Exception):
    pass


class ConfigError(ObsdnError):
    pass


class AuthError(ObsdnError):
    pass


class SignError(ObsdnError):
    pass


class ApiError(ObsdnError):
    def __init__(
        self,
        status: int,
        code: str = "",
        message: str = "",
        ref_code: str = "",
        request_id: str = "",
    ):
        self.status = status
        self.code = code
        self.message = message
        self.ref_code = ref_code
        self.request_id = request_id
        super().__init__(f"HTTP {status}: {code} - {message}")


class WsError(ObsdnError):
    pass
