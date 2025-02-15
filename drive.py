from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from googleapiclient.discovery import build

from exceptions import *
from platform import python_version

if int(python_version().split('.')[1]) >= 13: # python 3.13 or more
    from mimetypes import guess_file_type
    guess_type = guess_file_type
else: # python 3.12 or less
    from mimetypes import guess_type

class API:
    def __init__(self, service_account_file: str = 'credentials.json',
                 debug_mode: bool = False, **kwargs) -> None:
        
        if debug_mode and 'pretty_printer' in kwargs:
            self.pp = kwargs.get('pretty_printer')
        
        self.scopes = [
            'https://www.googleapis.com/auth/drive'
        ]

        self.account_fp = service_account_file

        self.credentials = service_account.Credentials.from_service_account_file(
            self.account_fp, scopes = self.scopes)
        self.service = build('drive', 'v3', credentials = self.credentials)
    
    def get_all_files(self):
        return self.service.files().list(pageSize = 10,
            fields = "nextPageToken, files(id, name, mimeType)") \
            .execute()

    def __resolve_mime_type(self, fp: str) -> str:
        return guess_type(fp, strict = False)[0]

    def upload_file(self, fp: str, name: str, **kwargs) -> dict | None:
        mimetype = self.__resolve_mime_type(fp)
        metadata = {
            "name": name
        }

        if mimetype:
            metadata['mimeType'] = mimetype
        if 'folder_id' in kwargs:
            metadata.update({
                "parents": [
                    kwargs.get('folder_id')
                ]
            })
        
        media = MediaFileUpload(fp, mimetype = mimetype, resumable = True)
        r = self.service.files().create(body = metadata, media_body = media,
                                        fields = 'id').execute()
        
        if 'id' in r:
            return r
        else:
            raise UploadFileError('Unknown response: %s' % r)
    
    def delete_file(self, file_id: str) -> dict | None:
        return self.service.files().delete(fileId = file_id).execute()
    
    def create_folder(self, name, **kwargs) -> dict | None:
        metadata = {
            "name": name, "mimeType": "application/vnd.google-apps.folder"
        }

        if 'folder_id' in kwargs:
            metadata.update({
                "parents": [ kwargs.get('folder_id') ]
            })
        
        r = self.service.files().create(body = metadata,
                                           fields = 'id').execute()
        
        if 'id' in r:
            return r
        else:
            raise CreateFolderError('Unknown response: %s' % r.text)
    
    def download_file(self, file_id: str, destination: str) -> None:
        request = self.service.files().get_media(fileId=file_id)
        fh = open(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if hasattr(self, 'pp'):
                self.pp.pprint(f"Download {int(status.progress() * 100)}% complete.")
        fh.close()
        
if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(
        indent = 4)
    api = API(debug_mode = True, pretty_printer = pp)
    pp.pprint(api.get_all_files())