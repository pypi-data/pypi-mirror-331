import requests

def fetch_user_profile(url):

    method = "GET"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    }
    payload = {}
    timeout = 10

    try:
        session = requests.Session()
        # if self.proxy:
        #     session.proxies = {
        #         "http": self.proxy,
        #         "https": self.proxy,
        #     }
        if method == "GET":

            resp = session.get(
                url, headers=headers, timeout=timeout, allow_redirects=True
            )

        # elif method.upper() == "POST":

        #     resp = requests.post(
        #         url,
        #         json=payload,
        #         headers=headers,
        #         timeout=self.timeout,
        #         allow_redirects=True,
        #     )

        return resp.status_code, resp.text
    except Exception as e:

        return None, None
    

url = "https://www.pinterest.com/frickcollection"
status_code, response = fetch_user_profile(url)
print(status_code, response)
