from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class CheckPasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.must_change_password and request.path not in [reverse('password_change'), reverse('logout'), reverse('loginv'),reverse('login')]:
                return redirect('password_change')
            elif not request.user.must_change_password and request.user.must_add_profile and request.path not in [reverse('add_profile'), reverse('logout'),reverse('loginv'),reverse('login')]:
                return redirect('add_profile')
        response = self.get_response(request)
        return response
    
class CacheControlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response

class EnsureLoggedOutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in [reverse('loginv'), reverse('registerv'),reverse('forget_password'),reverse('resend_activation_email'),reverse('index')]:
            return redirect('loginv')
        response = self.get_response(request)
        return response
