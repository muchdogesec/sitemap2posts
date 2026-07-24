from types import SimpleNamespace
import logging
import os

from requests.utils import CaseInsensitiveDict

logger = logging.getLogger(__name__)


class ScrapflyError(Exception):
    def __str__(self):
        return f"ScrapflyError: {super().__str__()}"


class ScrapflyResponse:
    """Adapts a Scrapfly `result` object to look like a `requests.Response`."""

    def __init__(self, result):
        self.status_code = result.status_code
        self.ok = 200 <= self.status_code < 400
        self.reason = getattr(result, "reason", "")
        content = result.content
        if isinstance(content, bytes):
            self.content = content
            self.text = content.decode("utf-8", errors="replace")
        else:
            self.text = content or ""
            self.content = self.text.encode("utf-8")
        self.headers = CaseInsensitiveDict(result.headers)


def fetch_with_scapfly(session, url, headers, use_scrapfly_asp=False):
    proxy_apikey = os.getenv("SCRAPFLY_API_KEY")
    logger.info(f"Fetching `{url}` via scrapfly.io")
    headers = dict((f"headers[{k}]", v) for k, v in headers.items())
    params = dict(
        **headers,
        key=proxy_apikey,
        url=url,
        country="us,ca,mx,gb,fr,de,au,at,be,hr,cz,dk,ee,fi,ie,se,es,pt,nl",
        retry=True
    )
    if use_scrapfly_asp:
        params["asp"] = "true"
    resp = session.get("https://api.scrapfly.io/scrape", params=params)
    json_data = resp.json()
    if resp.status_code != 200:
        raise ScrapflyError(json_data)
    result = SimpleNamespace(**json_data["result"])
    result.headers = getattr(result, "response_headers", {})
    if getattr(result, "format", None) in ["blob", "clob"]:
        blob_resp = session.get(result.content, params=dict(key=proxy_apikey))
        result.content = blob_resp.content
    return ScrapflyResponse(result)
