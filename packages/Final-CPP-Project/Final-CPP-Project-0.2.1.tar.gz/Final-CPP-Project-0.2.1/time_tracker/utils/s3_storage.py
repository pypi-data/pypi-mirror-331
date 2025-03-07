import boto3
import uuid
from django.conf import settings

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_file(self, file, folder="profile_pictures"):
        """
        S3에 파일을 업로드하고, 파일 URL을 반환합니다.
        :param file: 업로드할 파일 (InMemoryUploadedFile)
        :param folder: 버킷 내 폴더 (기본은 profile_pictures)
        :return: S3에 저장된 파일 URL
        """
        # 파일 확장자 추출
        file_extension = file.name.split('.')[-1]
        # 고유한 파일명 생성 (예: profile_pictures/uuid4.jpg)
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
         # ExtraArgs를 통해 업로드 시 공개 읽기 권한과 Content-Disposition을 inline으로 설정합니다.
        self.s3.upload_fileobj(
            file,
            self.bucket_name,
            unique_filename,
            ExtraArgs={
                'ContentDisposition': 'inline',
                'ContentType': file.content_type
            }
        )
        file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{unique_filename}"
        return file_url
