"""Opt-in maintenance routes for D1; disabled when DEPLOY_TOKEN is absent."""
import hmac
import json
import logging
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .environment import env

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def maintenance(request, operation):
    token = env('DEPLOY_TOKEN')
    if len(token) < 32:
        return HttpResponse(status=404)
    expected = ('Bearer ' + token).encode()
    if not hmac.compare_digest(request.headers.get('Authorization', '').encode(), expected):
        return HttpResponse(status=403)
    try:
        if operation == 'migrate':
            output = StringIO()
            call_command('migrate', interactive=False, no_color=True, stdout=output, stderr=output)
            return JsonResponse({'ok': True, 'output': output.getvalue()})
        if operation == 'create-admin':
            data = json.loads(request.body)
            username, password = data.get('username', ''), data.get('password', '')
            if not isinstance(username, str) or not isinstance(password, str) or not username or len(username) > 150:
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)
            User = get_user_model()
            # Never reset an existing user's password or privileges on a retry.
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists.'}, status=409)
            user = User(username=username, email=data.get('email', ''))
            validate_password(password, user=user)
            User.objects.create_superuser(username=username, email=user.email, password=password)
            return JsonResponse({'ok': True}, status=201)
        return HttpResponse(status=404)
    except (ValidationError, ValueError, TypeError) as exc:
        # Validation errors contain rules, never echo the submitted password.
        message = exc.messages if isinstance(exc, ValidationError) else ['Invalid request.']
        return JsonResponse({'error': message}, status=400)
    except Exception:
        logger.exception('Worker maintenance operation failed: %s', operation)
        return JsonResponse({'error': 'Operation failed. Check Worker logs before retrying.'}, status=500)


urlpatterns = [path('<str:operation>/', maintenance)]
