import time
import requests


DEFAULT_API = 'https://aetherpin.com/api/remote-telescope/live'
USER_AGENT = 'AetherPin-Connector/0.2.4'

# Retry config — survives flaky WiFi, ISP hiccups, brief server blips.
MAX_RETRIES = 4
BACKOFF = [0, 2, 5, 10]  # seconds before attempt 1, 2, 3, 4


def _headers(api_key: str) -> dict:
    return {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json',
    }


def _post_with_retry(api_url: str, headers: dict, payload: dict) -> dict:
    last_err = None
    for attempt in range(MAX_RETRIES):
        if BACKOFF[attempt] > 0:
            print(f'[api] Retrying in {BACKOFF[attempt]}s... (attempt {attempt + 1}/{MAX_RETRIES})')
            time.sleep(BACKOFF[attempt])
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
            # 4xx is a real client error — don't retry, surface immediately
            if 400 <= resp.status_code < 500:
                resp.raise_for_status()
            # 5xx or anything else — retry
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            # 4xx → bubble up, no more retries
            if e.response is not None and 400 <= e.response.status_code < 500:
                raise
            last_err = e
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            last_err = e
            print(f'[api] Network error: {type(e).__name__}')
    # All retries exhausted
    raise last_err if last_err else RuntimeError('Send failed (no error captured)')


def send_status(api_key: str, data: dict, api_url: str = DEFAULT_API) -> dict:
    return _post_with_retry(api_url, _headers(api_key), {
        'target_name': data['target_name'],
        'ra': data['ra'],
        'dec': data['dec'],
        'status': 'live',
    })


def send_offline(api_key: str, api_url: str = DEFAULT_API) -> dict:
    return _post_with_retry(api_url, _headers(api_key), {
        'target_name': '',
        'ra': '0',
        'dec': '0',
        'status': 'offline',
    })


def send_heartbeat(api_key: str, target_name: str, ra: str, dec: str, api_url: str = DEFAULT_API) -> dict:
    """Re-send current target to keep the live row warm (call every ~30-60 min)."""
    return _post_with_retry(api_url, _headers(api_key), {
        'target_name': target_name,
        'ra': ra,
        'dec': dec,
        'status': 'live',
    })
