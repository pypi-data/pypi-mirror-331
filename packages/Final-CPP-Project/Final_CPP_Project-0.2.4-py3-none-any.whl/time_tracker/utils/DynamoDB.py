import boto3
from botocore.exceptions import ClientError
from django.contrib.auth.decorators import login_required

# DynamoDB 리소스 객체 생성
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB 테이블 생성 함수 (한 번만 실행)
def create_tables():
    try:
        # Users 테이블 생성
        dynamodb.create_table(
            TableName='Users', # 생성할 테이블 이름
            KeySchema=[ # 테이블의 주요 키를 정의 (PK 정의)
                {
                    'AttributeName': 'ID', # 'ID' 필드가 기본 키 역할을 함
                    'KeyType': 'HASH'  # Primary key로 HASH 타입을 사용
                },
            ],
            AttributeDefinitions=[  # 테이블에서 사용할 속성(속성 이름과 속성 타입 정의)
                {
                    'AttributeName': 'ID',  # 'ID'는 기본 키로 사용되는 속성
                    'AttributeType': 'S'    # 'S'는 'String'을 의미, 즉 'ID'는 문자열 타입 (N : number / B : Binary)
                },
            ],
            BillingMode='PAY_PER_REQUEST'  # 요금 계산 방식: On-demand 모드 (요청에 따라 요금 부과)
        )
        print("Users table created successfully.")
    except ClientError as e:
        if 'ResourceInUseException' in str(e):
            print("Users table already exists.")
        else:
            print(f"Error creating Users table: {e}")

    try:
        # Worktime 테이블 생성
        dynamodb.create_table(
            TableName='Worktime',
            KeySchema=[
                {
                    'AttributeName': 'EntryID',
                    'KeyType': 'HASH'  # Primary key (EntryID)
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'EntryID',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand 모드
        )
        print("Worktime table created successfully.")
    except ClientError as e:
        if 'ResourceInUseException' in str(e):
            print("Worktime table already exists.")
        else:
            print(f"Error creating Worktime table: {e}")

    try:
        # Projects 테이블 생성
        dynamodb.create_table(
            TableName='Projects',
            KeySchema=[
                {
                    'AttributeName': 'ProjectID',
                    'KeyType': 'HASH'  # Primary key (ProjectID)
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ProjectID',
                    'AttributeType': 'S'
                },
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand 모드
        )
        print("Projects table created successfully.")
    except ClientError as e:
        if 'ResourceInUseException' in str(e):
            print("Projects table already exists.")
        else:
            print(f"Error creating Projects table: {e}")

# 테이블 생성 호출
create_tables()  # 테이블 생성 실행


# 회원가입 시 DynamoDB에 사용자 저장
def save_user_to_dynamodb(user_id, first_name, last_name, phone_number, email, picture):
    table = dynamodb.Table('Users')  # 이미 생성된 Users 테이블 사용
    table.put_item(
        Item={
            'ID': user_id,  # 사용자가 입력한 ID 값을 그대로 사용
            'FirstName': first_name,
            'LastName': last_name,
            'PhoneNumber': phone_number,
            'Email': email,
            'Picture': picture  # 프로필 사진 URL
        }
    )
    print(f"User {first_name} {last_name} added to Users table.")

# 프로필 사진 업데이트 시 DynamoDB에 사진 정보 업데이트
def update_user_picture(user_id, picture):
    table = dynamodb.Table('Users')  # Users 테이블 사용
    try:
        # ID는 문자열로 변환하여 업데이트
        table.update_item(
            Key={'ID': user_id},  # ID 필드를 user_id로 설정
            UpdateExpression="set Picture = :p",  # Picture 필드 업데이트
            ExpressionAttributeValues={':p': picture}  # Picture에 저장할 값
        )
        print(f"User {user_id} profile picture updated.")
    except ClientError as e:
        print(f"Error updating profile picture for user {user_id}: {e}")
        
# 업무 세션 종료 시 Worktime 테이블에 데이터 저장
def save_worktime_to_dynamodb(entry_id, user_id, project_id, start_time, end_time, target_time, overtime):
    # 날짜를 문자열로 변환
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None
    
    # EntryID를 문자열로 변환
    entry_id_str = str(entry_id)  # EntryID를 문자열로 변환하여 저장
    
    table = dynamodb.Table('Worktime')  # 이미 생성된 Worktime 테이블 사용
    table.put_item(
        Item={
            'EntryID': user_id,
            'UserID': user_id,
            'ProjectID': project_id,
            'StartTime': start_time_str,
            'EndTime': end_time_str,
            'TargetTime': target_time,
            'Overtime': overtime
        }
    )
    print(f"Worktime entry {entry_id} added to Worktime table.")

# 프로젝트 정보 Projects 테이블에 삽입
def save_project_to_dynamodb(project_id, project_name, description):
    table = dynamodb.Table('Projects')  # 이미 생성된 Projects 테이블 사용
    try:
        #project_id를 문자열로 변환하여 전달
        project_id_str = str(project_id)
        print(f"Saving project{project_name} with ID {project_id_str} to DynamoDB")
        table.put_item(
            Item={
                'ProjectID': project_id,
                'ProjectName': project_name,
                'Description': description
            }
        )
        print(f"Project {project_name} added to Projects table.")
    except ClientError as e:
        print(f"Error saving project {project_name} to DynamoDB: {e}")
