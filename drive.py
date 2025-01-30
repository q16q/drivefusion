import requests, logging, os
from dotenv import load_dotenv

class DriveAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.version = 'weekly'
        self.base_url = 'https://www.googleapis.com/drive/v3/'
        self.logger = logging.getLogger(__name__)

    def request(self, route: str, method: str, **kwargs):
        params = {
            "key": self.api_key,
            "v": self.version
        }

        if 'params' in kwargs:
            params.update(kwargs.get('params'))

        request = requests.request(
            method = method, url = self.base_url + route,
            params = params
        )
        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error(err)
        return request

if __name__ == '__main__': # test code
    load_dotenv()
    drive = DriveAPI(api_key = os.getenv('GOOGLE_API_KEY'))
    r = drive.request('files', 'GET')