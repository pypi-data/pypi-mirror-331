from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, WorkSession  # CustomUser 모델을 임포트

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # 이메일 필수
    first_name = forms.CharField(max_length=30, required=True)  # 이름 필수
    last_name = forms.CharField(max_length=30, required=True)  # 성 필수
    phone_number = forms.CharField(max_length=15, required=True)  # 전화번호 필수

    class Meta:
        model = CustomUser  # CustomUser 모델 사용
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)  # 기본 UserCreationForm 동작 수행
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()  # DB에 저장
        return user

class ProfilePictureForm(forms.Form):
    profile_picture = forms.ImageField()

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        # ✅ 파일 크기 제한 (5MB)
        if picture:
            max_size = 5 * 1024 * 1024  # 5MB
            if picture.size > max_size:
                raise forms.ValidationError("The uploaded file is too large (max 5MB).")

            # ✅ 확장자 확인 (JPG, PNG, GIF만 허용)
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = picture.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Only JPG, PNG, and GIF files are allowed.")

        return picture

class WorkSessionForm(forms.ModelForm):
    class Meta:
        model = WorkSession
        fields = ['project', 'target_minutes']
        labels = {
            'project': 'Select Project',
            'target_minutes': 'Set Target Time (in minutes)',  # ✅ 올바른 단위로 수정
        }
        widgets = {
            'target_minutes': forms.NumberInput(attrs={'step': '1', 'min': '1'}),  # ✅ 정수 입력으로 수정
        }
