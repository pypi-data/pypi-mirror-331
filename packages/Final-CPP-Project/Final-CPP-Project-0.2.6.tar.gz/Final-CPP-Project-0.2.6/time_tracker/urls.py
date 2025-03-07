from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home,
    signup,
    login_view,
    profile_view,
    dashboard_view,
    select_topic,
    work_session_view,
    project_detail_view,
    upload_profile_picture,
    edit_work_session,
    delete_work_session,  # ✅ delete_work_session을 임포트합니다.
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', signup, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('select_topic/', select_topic, name='select_topic'),
    path('work_session/<int:session_id>/', work_session_view, name='work_session'),
    path('project/<int:project_id>/', project_detail_view, name='project_detail'),
    path('upload-profile-picture/', upload_profile_picture, name='upload_profile_picture'),
    path('edit_work_session/<int:session_id>/', edit_work_session, name='edit_work_session'),
    path('work_session/<int:session_id>/delete/', delete_work_session, name='delete_work_session'),  # ✅ 삭제 경로 추가
]
