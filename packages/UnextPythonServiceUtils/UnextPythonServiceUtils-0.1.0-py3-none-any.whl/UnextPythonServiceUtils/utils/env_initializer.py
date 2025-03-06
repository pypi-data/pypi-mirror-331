from typing import Optional, cast
from ..ioc.singleton import SingletonMeta


class EnvStore(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._aws_access_key_id: Optional[str] = None
        self._aws_secret_access_key: Optional[str] = None
        self._bedrock_aws_region_name: Optional[str] = None
        self._aws_region_name: Optional[str] = None
        self._environment: Optional[str] = None
        self._domain: Optional[str] = None
        self._service_name: Optional[str] = None
        self._logging_filename: Optional[str] = None
        self._authorization: Optional[str] = None
        self._auth_token_algorithm: Optional[str] = None
        self._db_name: Optional[str] = None
        self._jwks_edunew: Optional[str] = None

    @property
    def aws_access_key_id(self) -> str:
        return cast(str, self._aws_access_key_id)

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: str) -> None:
        self._aws_access_key_id = value

    @property
    def aws_secret_access_key(self) -> str:
        return cast(str, self._aws_secret_access_key)

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: str) -> None:
        self._aws_secret_access_key = value

    @property
    def bedrock_aws_region_name(self) -> str:
        return cast(str, self._bedrock_aws_region_name)

    @bedrock_aws_region_name.setter
    def bedrock_aws_region_name(self, value: str) -> None:
        self._bedrock_aws_region_name = value

    @property
    def aws_region_name(self) -> str:
        return cast(str, self._aws_region_name)

    @aws_region_name.setter
    def aws_region_name(self, value: str) -> None:
        self._aws_region_name = value

    @property
    def environment(self) -> str:
        return cast(str, self._environment)

    @environment.setter
    def environment(self, value: str) -> None:
        self._environment = value

    @property
    def domain(self) -> str:
        return cast(str, self._domain)

    @domain.setter
    def domain(self, value: str) -> None:
        self._domain = value

    @property
    def service_name(self) -> str:
        return cast(str, self._service_name)

    @service_name.setter
    def service_name(self, value: str) -> None:
        self._service_name = value

    @property
    def logging_filename(self) -> str:
        return cast(str, self._logging_filename)

    @logging_filename.setter
    def logging_filename(self, value: str) -> None:
        self._logging_filename = value

    @property
    def authorization(self) -> str:
        return cast(str, self._authorization)

    @authorization.setter
    def authorization(self, value: str) -> None:
        self._authorization = value

    @property
    def auth_token_algorithm(self) -> str:
        return cast(str, self._auth_token_algorithm)

    @auth_token_algorithm.setter
    def auth_token_algorithm(self, value: str) -> None:
        self._auth_token_algorithm = value

    @property
    def db_name(self) -> str:
        return cast(str, self._db_name)

    @db_name.setter
    def db_name(self, value: str) -> None:
        self._db_name = value

    @property
    def jwks_edunew(self) -> str:
        return cast(str, self._jwks_edunew)

    @jwks_edunew.setter
    def jwks_edunew(self, value: str) -> None:
        self._jwks_edunew = value
