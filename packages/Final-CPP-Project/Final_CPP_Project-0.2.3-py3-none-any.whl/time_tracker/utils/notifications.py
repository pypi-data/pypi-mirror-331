import boto3
from django.conf import settings
from botocore.exceptions import ClientError

class SNSNotification:
    def __init__(self):
        """AWS SNS 클라이언트 생성"""
        self.client = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,  # 필요하지 않다면 제거 가능
            region_name=settings.AWS_REGION
        )
        self.topic_arn = settings.SNS_TOPIC_ARN

    def send_notification(self, message, subject="Work Session Update"):
        """SNS 알림을 전송하는 함수"""
        try:
            response = self.client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            print(f"✅ SNS Notification Sent: {response}")
            return response
        except ClientError as e:
            print(f"❌ Error sending SNS message: {e}")
            return None
