import urllib.request
import urllib.parse
import json

class State(object):
    def __init__(self, user_agent=None):
        self._user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        self._cookies = {}
        self._headers = {
            "User-Agent": self._user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.tiktok.com",
            "Referer": "https://www.tiktok.com/"
        }

    def setCookies(self, cookies):
        if isinstance(cookies, dict):
            self._cookies.update(cookies)
        elif isinstance(cookies, str):
            for part in cookies.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    self._cookies[k.strip()] = v.strip()

    def getCookies(self):
        return self._cookies

    def _getCookieHeader(self):
        return "; ".join([f"{k}={v}" for k, v in self._cookies.items()])

    def _request(self, method, url, params=None, data=None, headers=None):
        if params:
            qs = urllib.parse.urlencode(params)
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"

        req_headers = dict(self._headers)
        if headers:
            req_headers.update(headers)
        cookie_header = self._getCookieHeader()
        if cookie_header:
            req_headers["Cookie"] = cookie_header

        body = None
        if data is not None:
            if isinstance(data, (dict, list)):
                body = urllib.parse.urlencode(data).encode("utf-8")
                if "Content-Type" not in req_headers:
                    req_headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif isinstance(data, (bytes, bytearray)):
                body = bytes(data)
            elif isinstance(data, str):
                body = data.encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=req_headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_bytes = resp.read()
                set_cookie = resp.headers.get_all("Set-Cookie") or []
                for sc in set_cookie:
                    part = sc.split(";")[0]
                    if "=" in part:
                        k, v = part.split("=", 1)
                        self._cookies[k.strip()] = v.strip()
                try:
                    return json.loads(resp_bytes.decode("utf-8"))
                except Exception:
                    return resp_bytes
        except urllib.error.HTTPError as e:
            try:
                err_bytes = e.read()
                return json.loads(err_bytes.decode("utf-8"))
            except Exception:
                return {"error": str(e), "code": e.code}
        except Exception as e:
            return {"error": str(e)}

    def _get(self, url, params=None, headers=None):
        return self._request("GET", url, params=params, headers=headers)

    def _post(self, url, params=None, data=None, headers=None):
        return self._request("POST", url, params=params, data=data, headers=headers)
