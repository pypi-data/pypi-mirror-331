from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, WorkSession, Project
from .utils.DynamoDB import save_project_to_dynamodb  # DynamoDB에 저장하는 함수를 임포트

# 필요 없는 모델을 제거하려면 unregister를 사용합니다.
admin.site.unregister(Group)

# CustomUser 모델을 관리하는 관리자 클래스
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'date_joined', 'hourly_rate')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'hourly_rate')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'hourly_rate')}
        ),
    )

# WorkSession 모델에서 총 근무 시간을 계산하는 메서드 추가
def total_work_time(obj):
    """업무 세션의 총 근무 시간을 계산하여 반환"""
    if obj.start_time and obj.end_time:
        return obj.end_time - obj.start_time
    return None
total_work_time.short_description = '총 업무 시간'

# WorkSession 모델을 커스터마이징하여 추가 정보 표시
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'start_time', 'end_time', total_work_time, 'salary_display', 'display_is_deleted')
    list_filter = ('user', 'project', 'is_deleted')  # 'is_deleted' 필드로 필터링
    search_fields = ('user__username', 'project__name')

    def display_is_deleted(self, obj):
        """ 삭제된 항목을 'Yes' 또는 'No'로 표시 """
        return "Yes" if obj.is_deleted else "No"
    display_is_deleted.short_description = 'Deleted'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 삭제되지 않은 세션만 반환하고, 관리자는 삭제된 세션도 볼 수 있도록 처리
        return qs.filter(start_time__isnull=False)  # 삭제된 세션도 포함하려면 'is_deleted' 조건을 제거

    def salary_display(self, obj):
        """ 급여를 보기 좋게 표시 """
        salary = obj.get_salary()
        return f"${salary:.2f}"
    salary_display.short_description = 'Salary'

# Project 모델을 커스터마이징하여 삭제 상태 표시
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('is_deleted',)  # 'is_deleted' 필드로 필터링
    search_fields = ('name',)
    
    def save_model(self, request, obj, form, change):
        """
        프로젝트가 생성되거나 수정될 때마다 호출되는 메서드입니다.
        여기서 프로젝트 정보를 DynamoDB에 저장하도록 합니다.
        """
        super().save_model(request, obj, form, change)
        
        # 프로젝트가 생성되거나 수정될 때마다 DynamoDB에 저장
        save_project_to_dynamodb(
            project_id=str(obj.id),
            project_name=obj.name,
            description=obj.description
        )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(WorkSession, WorkSessionAdmin)