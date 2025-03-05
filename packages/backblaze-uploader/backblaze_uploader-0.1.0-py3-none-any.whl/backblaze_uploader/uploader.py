import b2sdk.v2 as b2
import os


class BackblazeB2Uploader:
    def __init__(self, application_key_id, application_key, bucket_name):
        """Backblaze B2 uploader class ni ishga tushirish"""
        self.info = b2.InMemoryAccountInfo()
        self.b2_api = b2.B2Api(self.info)
        self.b2_api.authorize_account(
            "production", application_key_id, application_key)
        self.bucket = self.b2_api.get_bucket_by_name(bucket_name)

    def upload_file(self, local_file_path, b2_file_name=None):
        """Local faylni Backblaze B2 bucket'ga yuklash"""
        try:
            if b2_file_name is None:
                b2_file_name = os.path.basename(local_file_path)

            uploaded_file = self.bucket.upload_local_file(
                local_file=local_file_path,
                file_name=b2_file_name,
                content_type=None,
                file_infos=None,
            )

            return {
                'file_id': uploaded_file.id_,
                'file_name': uploaded_file.file_name,
                'size': uploaded_file.size
            }
        except Exception as e:
            raise Exception(f"Upload xatosi: {str(e)}")

    def upload_multiple_files(self, file_paths):
        """Bir nechta faylni yuklash"""
        results = []
        for file_path in file_paths:
            result = self.upload_file(file_path)
            results.append(result)
        return results
