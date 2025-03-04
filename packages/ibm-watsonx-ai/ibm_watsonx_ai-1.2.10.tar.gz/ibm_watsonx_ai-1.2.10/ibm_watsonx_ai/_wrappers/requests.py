#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023-2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from __future__ import annotations

import os
import queue

import requests
import httpx
import json as js
import asyncio
import threading
from requests import packages, exceptions
from functools import wraps
import time
from random import random
from typing import Any, Iterator, AsyncIterator, Callable, TYPE_CHECKING
from contextlib import contextmanager, asynccontextmanager

if TYPE_CHECKING:
    from ibm_watsonx_ai import APIClient


HTTPX_DEFAULT_TIMEOUT = httpx.Timeout(timeout=600, connect=10)

HTTPX_KEEPALIVE_EXPIRY = 5
HTTPX_DEFAULT_LIMIT = httpx.Limits(
    max_connections=10,
    max_keepalive_connections=10,
    keepalive_expiry=HTTPX_KEEPALIVE_EXPIRY,
)

DEFAULT_RETRY_STATUS_CODES = [429, 503, 504, 520]
MAX_RETRY_DELAY = 8
DEFAULT_DELAY = 0.5

_MAX_RETRIES = 10  # number of retries after the first failure

additional_settings = {}
verify = None


def _httpx_transport_params(
    api_client: APIClient, retry_status_codes: list[int] | None = None
) -> dict:
    if not retry_status_codes:
        retry_status_codes = DEFAULT_RETRY_STATUS_CODES

    return {
        "_retry_status_codes": retry_status_codes,
        "verify": (
            api_client.credentials.verify
            or (verify == "True" if verify in ["True", "False"] else verify)
        ),
        "limits": HTTPX_DEFAULT_LIMIT,
    }


def set_verify_for_requests(func):
    @wraps(func)
    def wrapper(*args, **kw):
        global verify

        # Changing env variable has higher priority
        verify = os.environ.get("WX_CLIENT_VERIFY_REQUESTS") or verify

        if verify is not None:
            if verify == "True":
                kw.update({"verify": True})

            elif verify == "False":
                kw.update({"verify": False})

            else:
                kw.update({"verify": verify})

        else:
            kw.update({"verify": True})

        try:
            res = func(*args, **kw)

        except OSError as e:

            # User can pass verify the path to a CA_BUNDLE file or directory with certificates of trusted CAs
            if isinstance(verify, str) and verify != "False":
                raise OSError(
                    f"Connection cannot be verified with default trusted CAs. "
                    f"Please provide correct path to a CA_BUNDLE file or directory with "
                    f"certificates of trusted CAs. Error: {e}"
                )

            # forced verify to True
            elif verify:
                raise e

            # default
            elif verify is None:
                verify = "False"
                kw.update({"verify": False})
                res = func(*args, **kw)

            # disabled verify
            else:
                raise e

        return res

    return wrapper


def set_additional_settings_for_requests(func):
    @wraps(func)
    def wrapper(*args, **kw):
        kwargs = {}
        kwargs.update(additional_settings)
        kwargs.update(kw)
        return func(*args, **kwargs)

    return wrapper


@set_verify_for_requests
@set_additional_settings_for_requests
def get(url, params=None, **kwargs):
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.get(url=url, params=params, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def options(url, **kwargs):
    r"""Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.options(url=url, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def head(url, **kwargs):
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.head(url=url, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def post(url, data=None, json=None, **kwargs):
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    from ibm_watsonx_ai.utils.utils import _requests_convert_json_to_data

    data, json, kwargs = _requests_convert_json_to_data(data, json, kwargs)

    return requests.post(url=url, data=data, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def put(url, data=None, **kwargs):
    r"""Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    from ibm_watsonx_ai.utils.utils import _requests_convert_json_to_data

    data, json, kwargs = _requests_convert_json_to_data(
        data, kwargs.get("json"), kwargs
    )

    return requests.put(url=url, data=data, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    from ibm_watsonx_ai.utils.utils import _requests_convert_json_to_data

    data, json, kwargs = _requests_convert_json_to_data(
        data, kwargs.get("json"), kwargs
    )

    return requests.patch(url=url, data=data, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def delete(url, **kwargs):
    r"""Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.delete(url=url, **kwargs)


class Session(requests.Session):
    """A Requests session.

    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> import requests
      >>> s = requests.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>

    Or as a context manager::

      >>> with requests.Session() as s:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """

    def __init__(self):
        requests.Session.__init__(self)

    @set_verify_for_requests
    @set_additional_settings_for_requests
    def request(self, method, url, **kwargs):
        """Constructs a :class:`Request <Request>`, prepares it and sends it.
        Returns :class:`Response <Response>` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the
            :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the
            :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the
            :class:`Request`.
        :param files: (optional) Dictionary of ``'filename': file-like-objects``
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        :rtype: requests.Response
        """

        kwargs["method"] = method
        kwargs["url"] = url
        from ibm_watsonx_ai.utils.utils import _requests_convert_json_to_data

        data, json, kwargs = _requests_convert_json_to_data(
            kwargs.get("data"), kwargs.get("json"), kwargs
        )
        return super().request(**{**kwargs, **{"data": data}})


def session():
    """
    Returns a :class:`Session` for context-management.

    .. deprecated:: 1.0.0

        This method has been deprecated since version 1.0.0 and is only kept for
        backwards compatibility. New code should use :class:`~requests.sessions.Session`
        to create a session. This may be removed at a future date.

    :rtype: Session
    """
    return Session()


class HTTPXAsyncClient(httpx.AsyncClient):
    def __init__(self, verify: httpx._types.VerifyTypes | None = None, **kwargs: Any):
        super().__init__(
            verify=verify if verify is not None else bool(verify),
            timeout=kwargs.get("timeout") or HTTPX_DEFAULT_TIMEOUT,
            limits=kwargs.get("limits") or HTTPX_DEFAULT_LIMIT,
            **kwargs,
        )

    async def post(  # type: ignore[override]
        self,
        url: str,
        *,
        content: str | bytes | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        **kwargs: Any,
    ) -> httpx.Response:

        if json is not None and content is None:
            from ibm_watsonx_ai.utils.utils import NumpyTypeEncoder

            content = js.dumps(json, cls=NumpyTypeEncoder)

            if headers and not headers.get("Content-Type"):
                headers["Content-Type"] = "application/json"

        response = await super().post(
            url=url,
            content=content,
            headers=headers,
            params=params,
            **kwargs,
        )
        return response

    @asynccontextmanager
    async def post_stream(
        self,
        method: str,
        url: str,
        *,
        content: str | bytes | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[httpx.Response]:

        if json is not None and content is None:
            from ibm_watsonx_ai.utils.utils import NumpyTypeEncoder

            content = js.dumps(json, cls=NumpyTypeEncoder)

            if headers is not None and headers.get("Content-Type") is not None:
                headers["Content-Type"] = "application/json"

        async with super().stream(
            method=method,
            url=url,
            content=content,
            headers=headers,
            params=params,
            **kwargs,
        ) as response:
            try:
                yield response
            finally:
                await response.aclose()

    def __del__(self) -> None:
        try:
            # Closing the connection pool when the object is deleted
            asyncio.get_running_loop().create_task(self.aclose())
        except Exception:
            pass


@set_verify_for_requests
def get_async_client(
    transport: httpx.AsyncBaseTransport | None = None, **kwargs: Any
) -> HTTPXAsyncClient:
    return HTTPXAsyncClient(transport=transport, **kwargs)


def _get_client(
    client_class: HTTPXClient | HTTPXAsyncClient,
    transport_class: httpx.HTTPTransport | httpx.AsyncHTTPTransport,
    transport_params: dict,
    **kwargs: Any,
) -> HTTPXClient | HTTPXAsyncClient:
    """Generic internal function to create httpx client with transport, with or without `proxies` param."""

    if "proxies" in kwargs and "proxy" not in transport_params:
        proxy_mounts = {
            k + "://": transport_class(**(transport_params | {"proxy": v}))
            for k, v in kwargs["proxies"].items()
        }
        kwargs.pop("proxies")
        return client_class(mounts=proxy_mounts, **kwargs)
    else:
        transport = transport_class(**transport_params)
        return client_class(transport=transport, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def _get_async_client(transport_params: dict, **kwargs: Any) -> HTTPXAsyncClient:
    """Internal function to create async httpx client with transport, with or without `proxies` param."""
    return _get_client(
        HTTPXAsyncClient, AsyncHTTPXRetryTransport, transport_params, **kwargs
    )


def backoff_timeout(wx_delay_time, attempt):
    jitter = 1 + 0.25 * random()
    sleep_seconds = min(wx_delay_time * pow(2.0, attempt), MAX_RETRY_DELAY)
    return sleep_seconds * jitter


def _with_retry_stream(
    max_retries: int = _MAX_RETRIES,
    delay_time: float = DEFAULT_DELAY,
    retry_status_codes: list[int] = DEFAULT_RETRY_STATUS_CODES,
):
    """Decorator to retry the function if it encounters a 429 HTTP status."""

    def decorator(func):
        @wraps(func)
        @contextmanager  # Ensure the wrapped function remains a context manager
        def wrapper(self, *args, **kwargs):
            _exception = None
            response: httpx.Response | None = None
            wx_max_retries = int(
                self.max_retries or os.environ.get("WATSONX_MAX_RETRIES") or max_retries
            )
            wx_delay_time = (
                self.delay_time
                or float(os.environ.get("WATSONX_DELAY_TIME", 0.0))
                or delay_time
            )
            wx_retry_status_codes = (
                self.retry_status_codes
                or list(
                    map(
                        int,
                        os.environ.get("WATSONX_RETRY_STATUS_CODES")
                        .strip("[]")
                        .split(","),
                    )
                )
                if os.environ.get("WATSONX_RETRY_STATUS_CODES")
                else [] or retry_status_codes
            )
            for attempt in range(max_retries + 1):
                try:
                    if response is not None:
                        response.close()
                    with func(
                        self, *args, **kwargs
                    ) as response:  # Call the original context manager
                        if (
                            response.status_code in wx_retry_status_codes
                        ) and attempt != wx_max_retries:
                            rate_limit_remaining = int(
                                response.headers.get(
                                    "x-requests-limit-remaining",
                                    self.rate_limiter.capacity,
                                )
                            )
                            if rate_limit_remaining == 0:
                                self.rate_limiter.adjust_tokens(rate_limit_remaining)
                            else:
                                time.sleep(backoff_timeout(wx_delay_time, attempt))
                            self.rate_limiter.acquire()
                            continue  # Retry the request
                        yield response  # Successful response, return it
                        return  # Ensure we exit the loop after yielding
                except httpx.TimeoutException as e:
                    if attempt < max_retries:
                        time.sleep(backoff_timeout(wx_delay_time, attempt))
                    else:
                        _exception = e
            if _exception is not None:
                raise _exception

        return wrapper

    return decorator


class HTTPXClient(httpx.Client):
    """Wrapper for httpx Sync Client"""

    def __init__(self, verify: httpx._types.VerifyTypes | None = None, **kwargs: Any):
        super().__init__(
            verify=verify if verify is not None else bool(verify),
            timeout=kwargs.pop("timeout", None) or HTTPX_DEFAULT_TIMEOUT,
            limits=kwargs.pop("limits", None) or HTTPX_DEFAULT_LIMIT,
            **kwargs,
        )

    def post(  # type: ignore[override]
        self,
        url: str,
        *,
        content: str | bytes | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        **kwargs: Any,
    ) -> httpx.Response:

        if json is not None and content is None:
            from ibm_watsonx_ai.utils.utils import NumpyTypeEncoder

            content = js.dumps(json, cls=NumpyTypeEncoder)

            if headers is not None and headers.get("Content-Type") is not None:
                headers["Content-Type"] = "application/json"

        response = super().post(
            url=url,
            content=content,
            headers=headers,
            params=params,
            **kwargs,
        )
        return response

    @contextmanager
    def post_stream(
        self,
        method: str,
        url: str,
        *,
        content: str | bytes | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        **kwargs: Any,
    ) -> Iterator[httpx.Response]:

        if json is not None and content is None:
            from ibm_watsonx_ai.utils.utils import NumpyTypeEncoder

            content = js.dumps(json, cls=NumpyTypeEncoder)

            if headers is not None and headers.get("Content-Type") is not None:
                headers["Content-Type"] = "application/json"

        with super().stream(
            method=method,
            url=url,
            content=content,
            headers=headers,
            params=params,
            **kwargs,
        ) as response:

            try:
                yield response
            finally:
                response.close()

    def __del__(self) -> None:
        try:
            # Closing the connection pool when the object is deleted
            self.close()
        except Exception:
            pass


@set_verify_for_requests
def get_httpx_client(
    transport: httpx.BaseTransport | None = None, **kwargs: Any
) -> HTTPXClient:
    return HTTPXClient(transport=transport, **kwargs)


@set_verify_for_requests
@set_additional_settings_for_requests
def _get_httpx_client(transport_params: dict, **kwargs: Any) -> HTTPXAsyncClient:
    """Internal function to create basic httpx client with transport, with or without `proxies` param."""
    return _get_client(HTTPXClient, HTTPXRetryTransport, transport_params, **kwargs)


class HTTPXRetryTransport(httpx.HTTPTransport):
    """
    To handle retrying of HTTP requests with delays.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._retry_status_codes = kwargs.pop("_retry_status_codes", None)
        super().__init__(*args, **kwargs)


class AsyncHTTPXRetryTransport(httpx.AsyncHTTPTransport):
    """
    To handle retrying of Async HTTP requests with delays.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._retry_status_codes = kwargs.pop("_retry_status_codes", None)
        super().__init__(*args, **kwargs)

    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        """
        Custom handle response
        """
        if self._retry_status_codes is not None:
            retries = 0
            _exception = None
            response: httpx.Response | None = None
            while retries < _MAX_RETRIES + 1:
                timeout = False
                try:
                    if response is not None:
                        await response.aclose()
                    response = await super().handle_async_request(request)
                except httpx.TimeoutException as e:
                    timeout = True
                    _exception = e

                if (
                    timeout or response.status_code in self._retry_status_codes
                ) and retries != _MAX_RETRIES:
                    await asyncio.sleep(2**retries)
                    retries += 1
                else:
                    break

            if _exception is not None:
                raise _exception
        else:
            response = await super().handle_async_request(request)
        return response


def _with_retry(
    max_retries: int = _MAX_RETRIES,
    delay_time: float = DEFAULT_DELAY,
    retry_status_codes: list[int] = DEFAULT_RETRY_STATUS_CODES,
):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            retries = 0
            _exception = None
            response: httpx.Response | None = None
            wx_max_retries = int(
                self.max_retries or os.environ.get("WATSONX_MAX_RETRIES") or max_retries
            )
            wx_delay_time = (
                self.delay_time
                or float(os.environ.get("WATSONX_DELAY_TIME", 0.0))
                or delay_time
            )
            wx_retry_status_codes = (
                self.retry_status_codes
                or list(
                    map(
                        int,
                        os.environ.get("WATSONX_RETRY_STATUS_CODES")
                        .strip("[]")
                        .split(","),
                    )
                )
                if os.environ.get("WATSONX_RETRY_STATUS_CODES")
                else [] or retry_status_codes
            )
            while retries < wx_max_retries + 1:
                timeout = False
                try:
                    if response is not None:
                        response.close()
                    response = function(self, *args, **kwargs)
                except httpx.TimeoutException as e:
                    timeout = True
                    _exception = e
                if timeout:
                    time.sleep(backoff_timeout(wx_delay_time, retries))
                    self.rate_limiter.acquire()
                    retries += 1
                    continue

                if (
                    response.status_code in wx_retry_status_codes
                ) and retries != wx_max_retries:
                    rate_limit_remaining = int(
                        response.headers.get(
                            "x-requests-limit-remaining",
                            self.rate_limiter.capacity,
                        )
                    )
                    if rate_limit_remaining == 0:
                        self.rate_limiter.adjust_tokens(rate_limit_remaining)
                    else:
                        time.sleep(backoff_timeout(wx_delay_time, retries))
                    self.rate_limiter.acquire()
                    retries += 1
                else:
                    break

            if _exception is not None:
                raise _exception
            return response

        return wrapper

    return decorator


class TokenBucket:
    """Thread-safe rate limiter with dynamic token adjustments."""

    def __init__(self, rate, capacity):
        self.capacity = capacity  # Max tokens
        self.rate = rate  # Tokens per second
        self.tokens = capacity  # Start full
        self.lock = threading.Lock()
        self.last_refill = time.time()
        self.condition_lock = threading.Condition(self.lock)
        self.waiting_threads = queue.Queue()

    def refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        if new_tokens >= 1:  # Only update if at least one token is added
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

    def acquire(self):
        """Wait for a token and process threads in correct order."""
        thread_id = threading.get_ident()

        with self.condition_lock:
            # Add to queue if not already in front
            if (
                self.waiting_threads.empty()
                or self.waiting_threads.queue[-1] != thread_id
            ):
                self.waiting_threads.put(thread_id)

            while True:
                self.refill()

                # Allow thread to proceed only if it's at the front of the queue and tokens are available
                if self.tokens >= 1 and self.waiting_threads.queue[0] == thread_id:
                    self.waiting_threads.get()  # Remove from queue
                    self.tokens -= 1  # Consume token
                    self.condition_lock.notify()  # Wake next in line
                    return

                # Wait only until the next expected refill time
                next_refill = self.last_refill + (1 / self.rate)
                wait_time = max(0, next_refill - time.time())
                self.condition_lock.wait(wait_time)

    def adjust_tokens(self, remaining_tokens):
        """Adjust token count based on RateLimit-Remaining."""
        with self.lock:
            self.tokens = min(self.capacity, remaining_tokens)
