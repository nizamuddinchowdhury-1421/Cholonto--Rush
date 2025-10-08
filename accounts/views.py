from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .forms import CustomUserCreationForm, CustomPasswordChangeForm


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Cholonto--Rush!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def custom_logout(request):

    try:
        print(f"Logout view called. User authenticated: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'You have been successfully logged out.')
            return render(request, 'registration/logged_out.html')
        else:
            messages.info(request, 'You are not logged in.')
            return redirect('login')
    except Exception as e:
        print(f"Error in logout view: {e}")
        messages.error(request, 'An error occurred during logout.')
        return redirect('login')

def password_reset(request):

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token and send email
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                

                reset_url = f"http://{current_site.domain}/accounts/reset/{uid}/{token}/"
                

                subject = 'Password Reset - Cholonto--Rush'
                message = f"""
                Hello {user.username},
                
                You requested a password reset for your Cholonto--Rush account.
                
                Please click the link below to reset your password:
                {reset_url}
                
                If you didn't request this, please ignore this email.
                
                Best regards,
                Cholonto--Rush Team
                """
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                return redirect('password_reset_done')
                
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done(request):

    return render(request, 'registration/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')


def password_reset_complete(request):

    return render(request, 'registration/password_reset_complete.html')


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'registration/change_password.html', {'form': form})


def debug_logout(request):
    """Debug view to test logout functionality"""
    return render(request, 'debug_logout.html', {
        'user_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else 'Anonymous',
    })

