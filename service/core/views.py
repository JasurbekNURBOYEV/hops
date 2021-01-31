"""
Main views file.
We'll be implementing the base control units here.

"""
# --- START: IMPORTS
# built-in
# local
from service.core.factory import bot

# django-specific
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# other/external
import telebot
# --- END: IMPORTS


@csrf_exempt
def handle_webhook_requests(request):
    """
    Here we map incoming updates to our bot instance accordingly
    :param request: django request object
    :return: django JsonResponse object
    """
    if request.headers.get('content-type') == 'application/json':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return JsonResponse(dict(ok=True))
    else:
        return JsonResponse(dict(ok=False), status=400)
