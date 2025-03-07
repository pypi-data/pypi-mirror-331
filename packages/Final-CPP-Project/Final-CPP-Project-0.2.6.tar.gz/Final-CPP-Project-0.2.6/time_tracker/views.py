import datetime  # 현재 날짜 및 시간을 알 수 있는 모듈
from datetime import timedelta 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WorkSession, Project
from .forms import CustomUserCreationForm, WorkSessionForm
from django.db.models import Sum, ExpressionWrapper, F, DurationField
from django.db.models.functions import TruncMonth
from .forms import ProfilePictureForm #s3 bucket를 활용해서 사진 저장
from time_tracker.utils.s3_storage import S3Storage  # 새로 만든 s3_storage 모듈 > utils 에 init.py 있어야 모듈로 인식
from .utils.notifications import SNSNotification  # 새 라이브러리(AWS SNS) 임포트
from .utils.DynamoDB import save_user_to_dynamodb, update_user_picture, save_project_to_dynamodb, save_worktime_to_dynamodb  # DynamoDB 관련 함수 임포트

def home(request):
    return render(request, 'registration/home.html')

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            save_user_to_dynamodb( #DynamoDB에 저장되게 하기
                user_id=user.username, # user.username을 ID로 사용 (사용자가 입력한 아이디)
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                email=user.email,
                picture=user.profile_image_url  # 프로필 사진 URL 추가
            )
                
            login(request, user)  # 회원가입 후 자동 로그인
            messages.success(request, '회원가입이 성공적으로 완료되었습니다!')
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # 로그인 성공 시 대시보드 페이지로 이동
        else:
            messages.error(request, 'The ID or password is not valid..')
            return render(request, 'registration/home.html')
    return render(request, 'registration/home.html')

@login_required
def profile_view(request):
    latest_session = None  # 기본값 설정
    
    # 사용자가 work_sessions 속성을 갖고 있는지 확인 후 가져오기
    if hasattr(request.user, 'work_sessions'):
        latest_session = request.user.work_sessions.order_by('-id').first()
    
    return render(request, 'registration/profile.html', {
        'user': request.user,
        'latest_session': latest_session,
    })
    
@login_required
def dashboard_view(request):
    now = datetime.datetime.now()  # 현재 시간 가져오기
    projects = Project.objects.all()  # 모든 프로젝트 목록 가져오기
    work_sessions = WorkSession.objects.filter(user=request.user,is_deleted=False).order_by('-id')  # 사용자의 모든 WorkSession 조회

    # 현재 진행 중인 (미완료된) WorkSession 조회
    active_session = WorkSession.objects.filter(
        user=request.user,
        start_time__isnull=False,
        end_time__isnull=True
    ).first()

    # 목표 시간 입력 폼 처리 (POST 요청 시)
    if request.method == "POST":
        print("🔍 Received POST data:", request.POST)  # 🔍 POST 요청 데이터 확인
        form = WorkSessionForm(request.POST)

        if form.is_valid():
            # 새로운 WorkSession 객체 생성
            work_session = form.save(commit=False)
            work_session.user = request.user

            # target_minutes 값 가져오기 (POST에서 직접 추출)
            target_minutes = request.POST.get('target_hours')  # 🔥 여기서 가져옴
            if target_minutes:
                work_session.target_minutes = int(target_minutes)  # 🔥 int 변환 후 저장

            # 🔍 디버깅 로그 추가
            print("✅ Form cleaned data:", form.cleaned_data)
            print("✅ Target minutes received:", work_session.target_minutes)

            work_session.save()
            print("✅ WorkSession saved with target_minutes:", work_session.target_minutes)  # 🛠 저장 확인
            messages.success(request, f"Project '{work_session.project.name}' selected with target time: {work_session.target_minutes} minutes.")
            return redirect('work_session', session_id=work_session.id)
        else:
            print("❌ Form is not valid:", form.errors)

    else:
        form = WorkSessionForm()

    # 월별 총 근무시간 계산 (완료된 세션만)
    monthly_totals = WorkSession.objects.filter(
        user=request.user,
        start_time__isnull=False,
        end_time__isnull=False
    ).annotate(
        month=TruncMonth('start_time')  # start_time 기준으로 월 단위 그룹화
    ).values('month').annotate(
        total_duration=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))  # 총 근무시간 계산
    ).order_by('month')

    # 템플릿에 전달할 컨텍스트
    context = {
        'current_time': now,             # 현재 시간
        'projects': projects,            # 모든 프로젝트 목록
        'work_sessions': work_sessions,  # 사용자의 모든 WorkSession
        'monthly_totals': monthly_totals,  # 월별 총 근무시간
        'active_session': active_session,  # 진행 중인 세션
        'form': form,  # 목표 시간 입력 폼
    }
    return render(request, 'registration/dashboard.html', context)
    
# 프로젝트 선택: 신규 회원 등 WorkSession이 없는 경우에 사용됨
@login_required
def select_topic(request):
    if request.method == "POST":
        print(f"🔍 Received POST data: {request.POST}")  # 🛠 디버깅 로그 추가

        project_id = request.POST.get('project')  # 선택한 프로젝트 ID 가져오기
        target_minutes = request.POST.get('target_minutes')  # 🔥 목표 시간 가져오기

        print(f"✅ Extracted target_minutes: {target_minutes}")  # 🛠 디버깅 로그 추가

        if not project_id:
            messages.error(request, "프로젝트를 선택하세요.")
            return redirect('dashboard')

        project = Project.objects.filter(id=project_id).first()  # 해당 프로젝트 찾기

        if project:
            try:
                # target_minutes가 숫자가 아니거나 비어 있으면 None 처리
                target_minutes = int(target_minutes) if target_minutes and target_minutes.isdigit() else None
            except ValueError:
                target_minutes = None

            work_session = WorkSession.objects.create(
                user=request.user,
                project=project,
                target_minutes=target_minutes  # 🔥 목표 시간 저장
            )
            print(f"✅ WorkSession saved with target_minutes: {work_session.target_minutes}")  # 🛠 확인 로그 추가

            messages.success(request, f"'{project.name}' 프로젝트가 선택되었습니다! 목표 시간: {work_session.target_minutes}분")
            return redirect('work_session', session_id=work_session.id)

    return redirect('dashboard')
    
@login_required
def work_session_view(request, session_id):
    # 1. 현재 사용자의 WorkSession 객체를 session_id를 통해 가져옵니다. 삭제된 세션은 제외
    # WorkSession을 가져올 때 is_deleted 상태와 관계없이 가져오도록 수정
    work_session = WorkSession.objects.filter(id=session_id, user=request.user).first()
    # WorkSession이 없거나 삭제된 경우에는 404 대신 기본 work session 페이지로 리다이렉트
    if not work_session:
        return redirect('work_session', session_id=session_id)  # 삭제된 세션이라도 다시 work session으로 리다이렉트
    
    notifier = SNSNotification()  # SNS 알림 객체 생성

    print("📌 Fetched WorkSession:", work_session)
    print("📌 Target Minutes:", work_session.target_minutes)

    # ✅ GET 요청 시 hide_buttons 값 유지
    hide_buttons = request.session.get('hide_buttons', False)
    shortfall = None  
    formatted_total_time = None  
    formatted_overtime = None
    
    # ✅ End Work 이후에만 `formatted_total_time`과 `formatted_overtime`을 계산
    if work_session.start_time and work_session.end_time:
        total_seconds = (work_session.end_time - work_session.start_time).total_seconds()
        actual_minutes = int(total_seconds / 60)
        formatted_total_time = f"{actual_minutes // 60} hours {actual_minutes % 60} minutes"

        overtime_minutes = 0
        if work_session.target_minutes:
            overtime_minutes = max(0, actual_minutes - work_session.target_minutes)
        formatted_overtime = f"{overtime_minutes // 60} hours {overtime_minutes % 60} minutes"
        
    # 급여 계산
    salary = work_session.get_salary()

    if request.method == "POST":
        action = request.POST.get('action')
        print(f"🛠 Received POST action: {action}")
        
        # ✅ 사용자 정보 가져오기
        user_name = request.user.get_full_name() or "Unknown User"  # 전체 이름 (없으면 "Unknown User")
        user_id = request.user.username  # 사용자 아이디

        # ✅ "Start Work" 버튼 클릭 시
        if action == "start" and not work_session.start_time:
            print("✅ Start Work clicked! Setting start_time...")
            work_session.start_time = timezone.now()
            work_session.save(update_fields=['start_time'])
            work_session.refresh_from_db()

            # ✅ SNS 알림 전송 (Start Work 시)
            message = (
                f"🚀 Work session started!\n"
                f"User: {user_name} ({user_id})\n"  # ✅ 사용자 정보 포함
                f"Project: {work_session.project.name}\n"
                f"Start Time: {work_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            notifier.send_notification(message, subject="Work Session Started")

            return redirect('work_session', session_id=work_session.id)

        # ✅ "End Work" 버튼 클릭 시
        elif action == "end":
            print("🚀 End Work process started...")
            work_session.end_time = timezone.now()
            work_session.save(update_fields=['end_time'])
            work_session.refresh_from_db()
            print("🚀 End Work completed! New end_time:", work_session.end_time)
            
            # ✅ End Work 이후에만 총 작업 시간 및 초과 근무 시간 계산
            total_seconds = (work_session.end_time - work_session.start_time).total_seconds()
            actual_minutes = int(total_seconds / 60)
            formatted_total_time = f"{actual_minutes // 60} hours {actual_minutes % 60} minutes"

            overtime_minutes = 0
            if work_session.target_minutes:
                overtime_minutes = max(0, actual_minutes - work_session.target_minutes)
            formatted_overtime = f"{overtime_minutes // 60} hours {overtime_minutes % 60} minutes"

            print(f"📌 Shortfall after END: {shortfall}")
            print(f"📌 Overtime after END: {formatted_overtime}")
            
            # ✅ 목표 시간을 초과한 경우 SNS 알림 발송 추가
            if actual_minutes >= work_session.target_minutes:
                message = (
                    f"✅ Work session successfully completed!\n"
                    f"User: {user_name} ({user_id})\n"
                    f"Project: {work_session.project.name}\n"
                    f"Start Time: {work_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"End Time: {work_session.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Total Work Time: {formatted_total_time}\n" 
                    f"Overtime: {formatted_overtime}"
                )
                notifier.send_notification(message, subject="Work Session Completed")
            
            # ✅ 워크 세션 종료 후 DynamoDB에 정보 저장
            save_worktime_to_dynamodb(
                entry_id=request.user.username,
                user_id=request.user.username,
                project_id=work_session.project.id,
                start_time=work_session.start_time,
                end_time=work_session.end_time,
                target_time=work_session.target_minutes,
                overtime=work_session.get_overtime()  # 오버타임 계산해서 전달
                )
                
            # ✅ 버튼 숨기지 않음
            request.session['hide_buttons'] = False
            request.session.modified = True
            return redirect('work_session', session_id=work_session.id)

        # ✅ "End Anyway" 버튼 클릭 시
        elif action == "end_anyway":
            print("🚀 End Anyway clicked! Updating end_time...")
            work_session.end_time = timezone.now()
            work_session.save(update_fields=['end_time'])
            work_session.refresh_from_db()
            print("🚀 End Anyway completed! New end_time:", work_session.end_time)

            # ✅ `end_anyway` 버튼 클릭 시, shortfall을 None으로 설정하여 버튼 숨김
            shortfall = None
            request.session['hide_buttons'] = True
            request.session.modified = True  
            print(f"히든버튼 값 상태 : {request.session['hide_buttons']}")

            # ✅ SNS 알림 전송 (End Anyway 시)
            message = (
                f"⚠️ Work session ended early!\n"
                f"User: {user_name} ({user_id})\n"
                f"Project: {work_session.project.name}\n"
                f"Start Time: {work_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"End Time: {work_session.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Work Time: {formatted_total_time}\n" 
                f"Overtime: {formatted_overtime}"
            )
            notifier.send_notification(message, subject="Work Session Ended Early")
            
            # ✅ 워크 세션 종료 후 DynamoDB에 정보 저장
            save_worktime_to_dynamodb(
                entry_id=request.user.username,
                user_id=request.user.id,
                project_id=work_session.project.id,
                start_time=work_session.start_time,
                end_time=work_session.end_time,
                target_time=work_session.target_minutes,
                overtime=work_session.get_overtime()  # 오버타임 계산해서 전달
                )
            
            return redirect('work_session', session_id=work_session.id)

        elif action == "continue":
            print("🔄 Continue Work clicked! Removing end_time...")
            work_session.end_time = None
            work_session.save(update_fields=['end_time'])
            work_session.refresh_from_db()
            print("🔄 Continuing work. end_time reset.")

            # ✅ 목표 시간과 부족한 시간 계산
            total_seconds = (timezone.now() - work_session.start_time).total_seconds()
            actual_minutes = int(total_seconds / 60)

            if work_session.target_minutes:
                shortfall = max(0, work_session.target_minutes - actual_minutes)

            print(f"📌 Shortfall after CONTINUE: {shortfall}")

            # ✅ 메시지 추가 (영어)
            if shortfall > 0:
                message = f"⏳ You have worked for {actual_minutes} minutes, but your target is {work_session.target_minutes} minutes. You are short by {shortfall} minutes."
            else:
                message = f"✅ You have met or exceeded your target time! Total work time: {actual_minutes} minutes."

            messages.success(request, message)

            return redirect('work_session', session_id=work_session.id)

    # ✅ GET 요청 처리: 업무 기록 페이지에서 데이터를 계산합니다.
    total_time = None
    if work_session.start_time and work_session.end_time:
        total_seconds = (work_session.end_time - work_session.start_time).total_seconds()
        actual_minutes = int(total_seconds / 60)
        formatted_total_time = f"{actual_minutes // 60} hours {actual_minutes % 60} minutes"

        if work_session.target_minutes:
            shortfall = max(0, work_session.target_minutes - actual_minutes)
            overtime_minutes = max(0, actual_minutes - work_session.target_minutes)
            formatted_overtime = f"{overtime_minutes // 60} hours {overtime_minutes % 60} minutes"
            
    # 3-2. 사용자가 시작한 모든 WorkSession 기록을 프로젝트별로 정렬해서 조회 (추가 통계용)
    all_sessions = WorkSession.objects.filter(
        user=request.user, 
        start_time__isnull=False,
        is_deleted=False  # 삭제된 세션 제외
    ).order_by('project__name', '-created_at')

    # 3-3. 각 프로젝트별 총 업무시간 계산 (종료된 세션만 포함)
    project_totals = WorkSession.objects.filter(
        user=request.user,
        start_time__isnull=False,
        end_time__isnull=False,
        is_deleted=False  # 삭제된 세션 제외
    ).values('project__name', 'project__id').annotate(
        total_duration=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))
    )

    # 3-4. 각 프로젝트별 총 업무시간을 "X hours Y minutes" 형식으로 변환
    formatted_project_totals = []
    for item in project_totals:
        td = item['total_duration']
        total_seconds_pt = td.total_seconds()
        hours_pt = int(total_seconds_pt // 3600)
        minutes_pt = int((total_seconds_pt % 3600) // 60)
        formatted = f"{hours_pt} hours {minutes_pt} minutes"
        item['formatted_duration'] = formatted
        formatted_project_totals.append(item)

    # 3-5. 월별 총 근무시간 계산 (종료된 세션만), 그룹화 후 합계 계산
    monthly_totals = WorkSession.objects.filter(
        user=request.user,
        start_time__isnull=False,
        end_time__isnull=False,
        is_deleted=False  # 삭제된 세션 제외
    ).annotate(
        month=TruncMonth('start_time')
    ).values('month').annotate(
        total_duration=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))
    ).order_by('month')

    # 3-6. 각 월별 급여 계산: 시급(request.user.hourly_rate)에 따라 계산 (급여 = 총 근무시간(시간) * 시급)
    monthly_with_salary = []
    for item in monthly_totals:
        total_seconds_month = item['total_duration'].total_seconds()
        h_month = int(total_seconds_month // 3600)
        m_month = int((total_seconds_month % 3600) // 60)
        formatted_time = f"{h_month} hours {m_month} minutes"
        hourly_rate = float(request.user.hourly_rate) if request.user.hourly_rate else 0
        salary = (total_seconds_month / 3600) * hourly_rate
        item['formatted_time'] = formatted_time
        item['salary'] = salary
        monthly_with_salary.append(item)

    # 4. 활성 세션 여부 판단
    is_active = work_session.start_time is not None and work_session.end_time is None

    # 5. 목표 시간 (Target Minutes) 가져오기
    target_time = work_session.target_minutes if work_session.target_minutes else "Not Set"

    # 6. 컨텍스트 구성
    context = {
        'work_session': work_session,
        'total_time': formatted_total_time,           
        'all_sessions': all_sessions,                   
        'project_totals': formatted_project_totals,     
        'monthly_totals': monthly_with_salary,          
        'is_active': is_active,                         
        'target_time': target_time,                     
        'overtime': formatted_overtime,                           
        'shortfall': shortfall,                         
        'messages': messages.get_messages(request),  # 🚀 messages 추가하여 버튼 숨김 처리 가능
        'hide_buttons': hide_buttons,  # ✅ 세션 값 추가
        'salary' : work_session.get_salary(),
    }

    # 7. work_session.html 렌더링
    return render(request, 'registration/work_session.html', context)
    
@login_required
def edit_work_session(request, session_id):
    """ 프로젝트와 목표 시간을 다시 설정할 수 있도록 기존 WorkSession 삭제 """
    work_session = get_object_or_404(WorkSession, id=session_id, user=request.user)

    # 업무가 시작되지 않은 경우에만 수정 가능
    if not work_session.start_time:
        work_session.delete()  # 기존 세션 삭제
        messages.info(request, "Work session has been reset. Please select a new project and target time.")
        return redirect('dashboard')

    messages.error(request, "You cannot edit a session after starting work.")
    return redirect('work_session', session_id=session_id)
    
@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # 해당 프로젝트에 대해 start_time과 end_time이 모두 기록된 WorkSession 조회 및 세션별 근무시간(annotation)
    sessions = WorkSession.objects.filter(
        user=request.user,
        project=project,
        start_time__isnull=False,
        end_time__isnull=False
    ).exclude(is_deleted=True).annotate(  # is_deleted가 True인 세션은 제외
        session_duration=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
    ).order_by('-created_at')
    
    # 총 근무시간(프로젝트 전체) 집계
    aggregated = sessions.aggregate(
        total_duration=Sum('session_duration')
    )
    total_duration = aggregated.get('total_duration', timedelta())  # 기본값으로 timedelta() 설정
    formatted_total_duration = ""
    if total_duration:
        total_seconds = total_duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        formatted_total_duration = f"{hours} hours {minutes} minutes"
    
    # 각 세션별로 근무시간을 "X hours Y minutes" 형식으로 변환하여, 각 세션 인스턴스에 추가
    for s in sessions:
        if s.session_duration:
            sec = s.session_duration.total_seconds()
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s.formatted_duration = f"{h} hours {m} minutes"
        else:
            s.formatted_duration = "N/A"
    
    context = {
        'project': project,
        'sessions': sessions,
        'total_duration': formatted_total_duration,
    }
    return render(request, 'registration/project_detail.html', context)

#프로필 페이지에서 이미지를 올리면 s3 bucket으로 사진활용
@login_required
def upload_profile_picture(request):
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            # 프로필 사진 업데이트 
            file = form.cleaned_data['profile_picture']
            
            # S3Storage 클래스 이용해서 파일을 S3에 업로드합니다.
            s3_storage = S3Storage()
            file_url = s3_storage.upload_file(file)  # 파일 URL 반환
            
            # 여기서 request.user의 profile_image_url 필드에 S3 URL을 저장합니다.
            request.user.profile_image_url = file_url
            request.user.save()  # 사용자 객체를 저장하여 프로필 이미지 URL을 반영합니다.
            
            # DynamoDB 프로필 사진 업데이트
            # 여기에서 user_id로 request.user.id를 사용하고, picture로 file_url을 넘깁니다.
            update_user_picture(request.user.username, file_url)  # request.user.id와 file_url 전달
            
            return redirect('profile')
    else:
        form = ProfilePictureForm()  # GET 요청일 경우 빈 폼을 전달합니다.
        
    return render(request, 'registration/upload_picture.html', {'form': form})  # 템플릿을 렌더링합니다.
    
@login_required
def delete_work_session(request, session_id):
    # 세션을 가져옵니다.
    work_session = get_object_or_404(WorkSession, id=session_id, user=request.user)
    
    # 세션의 'is_deleted'를 True로 설정하여 논리적 삭제
    work_session.is_deleted = True
    work_session.save()

    # 성공 메시지
    messages.success(request, "Work session deleted successfully.")

    # 프로젝트 상세 페이지로 리다이렉트
    return redirect('project_detail', project_id=work_session.project.id)