import requests


DEFAULT_API = 'https://aetherpin.com/api/remote-telescope/live'
USER_AGENT = 'AetherPin-Connector/0.2.3'


def _headers(api_key: str) -> dict:
    return {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json',
    }


def send_status(api_key: str, data: dict, api_url: str = DEFAULT_API) -> dict:
    resp = requests.post(
        api_url,
        headers=_headers(api_key),
        json={
            'target_name': data['target_name'],
            'ra': data['ra'],
            'dec': data['dec'],
            'status': 'live',
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def send_offline(api_key: str, api_url: str = DEFAULT_API) -> dict:
    resp = requests.post(
        api_url,
        headers=_headers(api_key),
        json={
            'target_name': '',
            'ra': '0',
            'dec': '0',
            'status': 'offline',
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
