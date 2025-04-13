# main/views.py

import os
import logging
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

def ban_view(request):
    # This view corresponds to the /ban endpoint.
    # It simply returns a 403 Forbidden response.
    return HttpResponseForbidden("Forbidden")

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

public_domain = os.environ.get('HOSTNAME')

@login_required
def services(request):
    logging.info(f"User {request.user.id} accessed the services page")
    return render(request, 'services.html')

@login_required
def nextcloud(request):
    logging.info(f"User {request.user.id} clicked Nextcloud")
    # Redirect to the external Nextcloud service.
    return redirect(f"https://{public_domain}/nextcloud")

@login_required
def jellyfin(request):
    logging.info(f"User {request.user.id} clicked Jellyfin")
    # Redirect to the external Jellyfin service.
    return redirect(f"https://{public_domain}/jellyfin/")

def ghostblog(request):
    logging.info(f"User {request.user.id} clicked GhostLog")
    # Redirect to the external Wordpress service.
    return redirect(f"https://{public_domain}/GhostLog")

def blog(request):
    return render(request, 'blog.html')

def favicon(request):
    # Serve the favicon from the static files. Here we assume your favicon.ico
    # is located in the "main/static" directory.
    favicon_path = os.path.join(settings.BASE_DIR, 'main', 'static', 'favicon.ico')
    return FileResponse(open(favicon_path, 'rb'), content_type='image/vnd.microsoft.icon')
