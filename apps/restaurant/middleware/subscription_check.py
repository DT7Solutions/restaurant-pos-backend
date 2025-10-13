# your_app/middleware/subscription_check.py
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages

class SubscriptionCheckMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip if user not logged in or admin site
        if not request.user.is_authenticated or request.path.startswith('/admin/'):
            return None

        # Superusers always allowed
        if request.user.is_superuser:
            return None

        # Check user subscription
        if not request.user.has_active_subscription:
            messages.error(request, "Your restaurant subscription has expired. Please renew to continue.")
            return redirect('subscription_expired_page')  
        return None
