import requests


DEFAULT_API = 'https://aetherpin.com/api/remote-telescope/live'


def send_status(api_key: str, data: dict, api_url: str = DEFAULT_API) -> dict:
    resp = requests.post(
        api_url,
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'target_name': data['target_name'],
            'ra': data['ra'],
            'dec': data['dec'],
            'status': 'live',
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def send_offline(api_key: str, api_url: str = DEFAULT_API) -> dict:
    resp = requests.post(
        api_url,
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'target_name': '',
            'ra': '0',
            'dec': '0',
            'status': 'offline',
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
