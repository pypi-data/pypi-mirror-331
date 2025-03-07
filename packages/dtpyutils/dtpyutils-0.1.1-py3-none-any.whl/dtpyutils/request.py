import logging
import requests
from .exception import RequestException


def internal_request(
        host: str,
        auth_key: str,
        auth_value: str,
        auth_type: str,
        method: str,
        path: str,
        disable_caching: bool = True,
        json_return: bool = True,
        has_success_response: bool = True,
        **kwargs,
):
    error_details = {
        'subject': f'Internal Request to {host}',
        'controller': f'request_to_{host}',
        'payload': {
            'host': host,
            'auth_key': auth_key,
            'auth_type': auth_type,
            'method': method,
            'path': path,
            'json_return': json_return,
            'success_checking': has_success_response,
        }
    }

    url = f'{host}/{path}'

    if auth_type == 'params' and 'params' in kwargs:
        kwargs['params'][auth_key] = auth_value
    elif auth_type == 'headers' and 'headers' in kwargs:
        kwargs['headers'][auth_key] = auth_value

    if disable_caching:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers'].update({
            'Cache-Control': 'private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        })

    try:
        response = requests.request(method=method, url=url, **kwargs)
    except Exception as e:
        logging.error(
            msg="We faced an error while we wanted to send an internal request.",
            extra={
                'details': error_details
            }
        )
        raise RequestException(
            status_code=500,
            message='Internal Request Error.',
            controller=f'request_to_{host}',
            skip_footprint=True,
        )

    if json_return:
        try:
            response_json = response.json()
        except Exception as e:
            error_details['payload']['text'] = response.text
            logging.error(
                msg="We faced an incorrect response from an internal service.",
                extra={
                    'details': error_details
                }
            )
            raise RequestException(
                status_code=500,
                message='Internal Request Error.',
                controller=f'request_to_{host}',
                skip_footprint=True,
            )

        if has_success_response:
            is_success = response_json.get('success', False) if isinstance(response_json, dict) else False
            return is_success, response_json.get('data' if is_success else 'message')

    return True, response.text
