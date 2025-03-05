from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    """ 사용자 모델: 프로필 이미지, 전화번호, 시급 정보 포함 """
    profile_image_url = models.URLField(default="https://placebear.com/150/150", blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0)
    REQUIRED_FIELDS = ['email']  # 이메일을 필수 필드로 지정

    def __str__(self):
        return self.username

class Project(models.Model):
    """ 프로젝트 모델: 프로젝트 이름 및 설명 포함 """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)  # 삭제된 프로젝트를 표시하는 필드
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일
    updated_at = models.DateTimeField(auto_now=True)  # 수정일

    def __str__(self):
        return self.name

class WorkSession(models.Model):
    """ 업무 세션 모델: 사용자, 프로젝트, 근무시간, 목표시간 관리 """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='work_sessions'  # 🚀 기존 'sessions' → 'work_sessions'로 변경!
    )
    
    project = models.ForeignKey(
        'Project', 
        on_delete=models.CASCADE, 
        related_name='work_sessions'  # 🚀 기존 'sessions' → 'work_sessions'로 변경!
    )
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    target_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="목표 시간(분 단위)"
    )

    is_deleted = models.BooleanField(default=False)  # 삭제된 세션을 표시하는 필드

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.start_time} - {self.end_time})"

    def get_duration(self):
        """ 실제 근무 시간 반환 (timedelta) """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def get_duration_display(self):
        """ 근무 시간을 'X hours Y minutes' 형식으로 변환 """
        duration = self.get_duration()
        if duration:
            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours} hours {minutes} minutes"
        return "Not started"

    def get_salary(self):
        """ 근무 시간을 기반으로 급여 계산 """
        duration = self.get_duration()
        if duration and self.user and self.user.hourly_rate is not None:
            total_hours = duration.total_seconds() / 3600
            return round(total_hours * float(self.user.hourly_rate), 2)
        return 0

    def get_target_time_display(self):
        """ 목표 시간을 'X hours Y minutes' 형식으로 변환 """
        if self.target_minutes and self.target_minutes > 0:
            hours = self.target_minutes // 60
            minutes = self.target_minutes % 60
            return f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"
        return "No target set"

    def has_exceeded_target(self):
        """ 목표 시간을 초과했는지 확인 """
        duration = self.get_duration()
        if duration and self.target_minutes:
            actual_minutes = duration.total_seconds() / 60
            return actual_minutes > self.target_minutes
        return False

    def get_overtime(self):
        """ 초과 근무 시간이 있으면 반환 ('X hours Y minutes' 형식) """
        duration = self.get_duration()
        if duration and self.target_minutes:
            actual_minutes = duration.total_seconds() / 60
            overtime = actual_minutes - self.target_minutes
            if overtime > 0:
                hours = int(overtime // 60)
                minutes = int(overtime % 60)
                return f"{hours} hours {minutes} minutes"
        return "No overtime"
        
    def delete(self, *args, **kwargs):
        """ 삭제 시 실제 삭제 대신 is_deleted를 True로 설정 """
        self.is_deleted = True
        self.save()  # 객체를 저장하여 'is_deleted' 값을 업데이트
        return None  # 실제 삭제하지 않