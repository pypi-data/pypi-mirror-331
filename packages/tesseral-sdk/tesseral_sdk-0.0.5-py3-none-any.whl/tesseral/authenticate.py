from typing import Optional, List, Dict
import time
import base64

from cryptography.exceptions import InvalidSignature
from httpx import Client, AsyncClient
from pydantic import BaseModel, ValidationError
from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1, \
    EllipticCurvePublicNumbers, EllipticCurvePublicKey, ECDSA
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives.hashes import SHA256

from .types.access_token_claims import AccessTokenClaims


class InvalidAccessTokenException(Exception):
    pass


class AsyncTesseralAuthenticator:
    _publishable_key: str
    _config_api_host: str
    _http_client: AsyncClient
    _jwks: Optional[Dict[str, EllipticCurvePublicKey]]
    _jwks_next_refresh_unix_seconds: float
    _jwks_refresh_interval_seconds: int

    def __init__(self, *, publishable_key: str,
                 config_api_host: str = "config.tesseral.com", jwks_refresh_interval_seconds: int = 3600):
        self._publishable_key = publishable_key
        self._config_api_host = config_api_host
        self._http_client = AsyncClient()
        self._jwks = None
        self._jwks_refresh_interval_seconds = jwks_refresh_interval_seconds
        self._jwks_next_refresh_unix_seconds = 0

    async def authenticate_access_token(self, *, access_token: str,
                                        now_unix_seconds: Optional[float] = None) -> AccessTokenClaims:
        if self._jwks is None or time.time() > self._jwks_next_refresh_unix_seconds:
            self._jwks = await self._fetch_jwks()
            self._jwks_next_refresh_unix_seconds = time.time() + self._jwks_refresh_interval_seconds

        return _authenticate_access_token(jwks=self._jwks, access_token=access_token, now_unix_seconds=now_unix_seconds)

    async def _fetch_jwks(self) -> Dict[str, EllipticCurvePublicKey]:
        response = await self._http_client.get(f"https://{self._config_api_host}/v1/config/{self._publishable_key}")
        response.raise_for_status()
        return _parse_jwks(response.text)


class TesseralAuthenticator:
    _publishable_key: str
    _config_api_host: str
    _http_client: Client
    _jwks: Optional[Dict[str, EllipticCurvePublicKey]]
    _jwks_next_refresh_unix_seconds: float
    _jwks_refresh_interval_seconds: int

    def __init__(self, *, publishable_key: str,
                 config_api_host: str = "config.tesseral.com", jwks_refresh_interval_seconds: int = 3600):
        self._publishable_key = publishable_key
        self._config_api_host = config_api_host
        self._http_client = Client()
        self._jwks = None
        self._jwks_refresh_interval_seconds = jwks_refresh_interval_seconds
        self._jwks_next_refresh_unix_seconds = 0

    def authenticate_access_token(self, *, access_token: str,
                           now_unix_seconds: Optional[float] = None) -> AccessTokenClaims:
        if self._jwks is None or time.time() > self._jwks_next_refresh_unix_seconds:
            self._jwks = self._fetch_jwks()
            self._jwks_next_refresh_unix_seconds = time.time() + self._jwks_refresh_interval_seconds

        return _authenticate_access_token(jwks=self._jwks, access_token=access_token, now_unix_seconds=now_unix_seconds)

    def _fetch_jwks(self) -> Dict[str, EllipticCurvePublicKey]:
        response = self._http_client.get(f"https://{self._config_api_host}/v1/config/{self._publishable_key}")
        response.raise_for_status()
        return _parse_jwks(response.text)


def _authenticate_access_token(jwks: Dict[str, EllipticCurvePublicKey], access_token: str, now_unix_seconds: Optional[float] = None) -> AccessTokenClaims:
    parts = access_token.split('.')
    if len(parts) != 3:
        raise InvalidAccessTokenException()

    raw_header, raw_claims, raw_signature = parts
    try:
        parsed_header = _AccessTokenHeader.model_validate_json(_base64_url_decode(raw_header))
        parsed_signature = _base64_url_decode(raw_signature)
    except ValidationError:
        raise InvalidAccessTokenException()

    try:
        public_key = jwks[parsed_header.kid]
    except KeyError:
        raise InvalidAccessTokenException()

    if len(parsed_signature) != 64:
        raise InvalidAccessTokenException()

    r = int.from_bytes(parsed_signature[:32], byteorder='big')
    s = int.from_bytes(parsed_signature[32:], byteorder='big')
    signature = encode_dss_signature(r, s)
    try:
        public_key.verify(signature, (raw_header + '.' + raw_claims).encode(),
                          ECDSA(SHA256()))
    except InvalidSignature:
        raise InvalidAccessTokenException()

    try:
        parsed_claims = AccessTokenClaims.model_validate_json(_base64_url_decode(raw_claims))
    except ValidationError:
        raise InvalidAccessTokenException()

    if now_unix_seconds is None:
        now_unix_seconds = time.time()

    # type assertions to appease mypy
    assert parsed_claims.nbf, InvalidAccessTokenException()
    assert parsed_claims.exp, InvalidAccessTokenException()
    if now_unix_seconds < parsed_claims.nbf or now_unix_seconds > parsed_claims.exp:
        raise InvalidAccessTokenException()

    return parsed_claims


def _parse_jwks(jwks_json: str) -> Dict[str, EllipticCurvePublicKey]:
    jwks_parsed = _JSONWebKeySet.model_validate_json(jwks_json)
    jwks = {}
    for json_web_key in jwks_parsed.keys:
        assert json_web_key.kty == 'EC'
        assert json_web_key.crv == 'P-256'

        x = int.from_bytes(_base64_url_decode(json_web_key.x), byteorder='big')
        y = int.from_bytes(_base64_url_decode(json_web_key.y), byteorder='big')
        public_key = EllipticCurvePublicNumbers(curve=SECP256R1(), x=x, y=y).public_key()
        jwks[json_web_key.kid] = public_key

    return jwks


def _base64_url_decode(s: str) -> bytes:
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


class _AccessTokenHeader(BaseModel):
    alg: str
    kid: str


class _JSONWebKey(BaseModel):
    kid: str
    kty: str
    crv: str
    x: str
    y: str

class _JSONWebKeySet(BaseModel):
    keys: List[_JSONWebKey]


