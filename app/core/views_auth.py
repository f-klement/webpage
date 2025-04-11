# core/views_auth.py

import os
import logging

from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives

from core.models import User

# Helper functions for token generation and confirmation
def generate_confirmation_token(user):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    # The token includes both the user ID and the email.
    return serializer.dumps({'user_id': user.id, 'email': user.email}, salt='email-confirm-salt')

def confirm_token(token, expiration=2592000):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
    except Exception:
        return None
    return data  # Expected to be a dict with 'user_id' and 'email'

def send_email(subject, recipient_list, plaintext_content, html_content):
    """
    Convenience function to send an email with both plaintext and HTML alternatives.
    """
    # Create the email message
    email_message = EmailMultiAlternatives(subject, plaintext_content, settings.DEFAULT_FROM_EMAIL, recipient_list)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

# Registration view.
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Check if username already exists.
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect(reverse("auth_register"))
        
        # Create a new user. Using create_user automatically hashes the password.
        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.email_confirmed = False
        new_user.admin_approved = False
        new_user.save()
        
        # Generate tokens and URLs for email confirmation and admin approval.
        # Generate tokens
        token = generate_confirmation_token(new_user)
        admin_token = generate_confirmation_token(new_user) # Can reuse the same token type

        # --- URL Generation ---
        # 1. Get relative paths using reverse()
        relative_confirm_path = reverse("auth_confirm", kwargs={"token": token})
        relative_approve_path = reverse("auth_approve", kwargs={"token": admin_token})

        # 2. Get the public facing domain name (MUST be set in your .env)
        #    Use the same variable Traefik uses, e.g., HOSTNAME
        public_domain = os.environ.get('HOSTNAME')

        # 3. Check if domain is set and construct HTTPS URLs
        if public_domain:
            confirm_url = f"https://{public_domain}{relative_confirm_path}"
            approve_url = f"https://{public_domain}{relative_approve_path}"
        else:
            # Fallback (will likely still be HTTP) or handle error
            messages.error(request, "Server configuration error: HOSTNAME environment variable not set.")
            logging.error("CRITICAL: HOSTNAME environment variable not set for URL generation.")
            # Maybe redirect back with error, or use a default that might fail
            # Forcing a potentially wrong URL is bad, better to error out here.
            # As a last resort fallback (use with caution):
            # confirm_url = request.build_absolute_uri(relative_confirm_path)
            # approve_url = request.build_absolute_uri(relative_approve_path)
            # Or simply:
            return redirect(reverse("auth_register")) # Redirect back with error message shown

        # Prepare email subjects and message content.
        subject_user = "Please confirm your email"
        subject_admin = "New user registration approval required"
        
        # Plaintext versions.
        plaintext_user = (
            f"Welcome, {username}!\n\n"
            f"Please confirm your email by clicking the following link:\n{confirm_url}"
        )
        plaintext_admin = (
            f"A new user has registered with the email {email}.\n\n"
            f"Please review and approve their account by clicking the following link:\n{approve_url}"
        )
        
        # HTML versions.
        html_user = f"""
        <p>Welcome, {username}!</p>
        <p>Please confirm your email by clicking on the following link:</p>
        <p><a href="{confirm_url}">{confirm_url}</a></p>
        """
        html_admin = f"""
        <p>Hey, localghost admin!</p>
        <p>A new user has registered with the username {username} and the email {email}.</p>
        <p>Please review and approve their account by clicking on the following link:</p>
        <p><a href="{approve_url}">{approve_url}</a></p>
        """
        
        # Send confirmation email to user.
        send_email(subject_user, [email], plaintext_user, html_user)
        
        # Notify admin for account approval.
        admin_email = os.environ.get("ADMIN_EMAIL")
        if admin_email:
            send_email(subject_admin, [admin_email], plaintext_admin, html_admin)
        
        messages.success(
            request,
            "Registration successful! Please check your email to confirm your account. Your account will be activated after admin approval."
        )
        return redirect(reverse("auth_login"))
        
    return render(request, "register.html")

# Email confirmation view.
def confirm_email(request, token):
    data = confirm_token(token)
    if not data:
        messages.error(request, "The confirmation link is invalid or has expired.")
        return redirect(reverse("auth_login"))
    
    try:
        user = User.objects.get(id=data.get('user_id'))
    except User.DoesNotExist: # type: ignore[attr-defined]
        messages.error(request, "User not found.")
        return redirect(reverse("auth_login"))
    
    # Verify that the email in the token matches the user's email.
    if user.email != data.get('email'):
        messages.error(request, "Email does not match.")
        return redirect(reverse("auth_login"))
    
    if user.email_confirmed:
        messages.success(request, "Account already confirmed. Please login.")
    else:
        user.email_confirmed = True
        user.save()
        messages.success(request, "You have confirmed your email. Your account is now pending admin approval.")
    
    return redirect(reverse("auth_login"))

# Admin approval view.
def approve_account(request, token):
    data = confirm_token(token)
    if not data:
        messages.error(request, "The approval link is invalid or has expired.")
        return redirect(reverse("auth_login"))
    
    try:
        user = User.objects.get(id=data.get('user_id'))
    except User.DoesNotExist: # type: ignore[attr-defined]
        messages.error(request, "User not found.")
        return redirect(reverse("auth_login"))
    
    if user.email != data.get('email'):
        messages.error(request, "Email mismatch.")
        return redirect(reverse("auth_login"))
    
    if user.admin_approved:
        messages.success(request, "Account already approved.")
    else:
        user.admin_approved = True
        user.save()
        messages.success(request, "User account approved.")
    
    return redirect(reverse("auth_login"))

# Login view.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Use Django's authentication system.
        user = authenticate(request, username=username, password=password)
        
        if not user:
            messages.error(request, "Invalid username or password.")
            return redirect(reverse("auth_login"))
        
        # Check confirmation and admin approval status.
        if not user.email_confirmed:
            messages.warning(request, "Please confirm your email address before logging in.")
            return redirect(reverse("auth_login"))
        
        if not user.admin_approved:
            messages.warning(request, "Your account is pending admin approval.")
            return redirect(reverse("auth_login"))
        
        # Log the user in.
        auth_login(request, user)
        messages.success(request, "Login successful!")
        return redirect(reverse("index"))
    
    return render(request, "login.html")

# Logout view.
@login_required
def logout(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect(reverse("index"))
