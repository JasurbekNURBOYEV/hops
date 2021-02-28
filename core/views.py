"""
Main views file.
We'll be implementing the base control units here.

"""
# --- START: IMPORTS
# built-in
# local
import json
import random
import traceback
from datetime import timedelta

from django.db.models import F, Q
from django.shortcuts import render
from django.utils import timezone

from core import models
from core.factory import bot

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
        print("processing...")
        try:
            bot.process_new_updates([update])
        except:
            print(traceback.format_exc())
        return JsonResponse(dict(ok=True))
    else:
        return JsonResponse(dict(ok=False), status=400)


def show_stats(request, *args, **kwargs):
    a_month_before_date = timezone.now() - timedelta(days=30)
    today = timezone.now()
    codes_for_last_month = models.Code.filter(created_time__gte=a_month_before_date, created_time__lte=today)
    code_by_days = []
    for i in range(30):
        day = a_month_before_date + timedelta(days=i)
        codes_for_the_day = codes_for_last_month.filter(created_time__lte=day)
        # calculate error percentage
        error_codes = codes_for_the_day.filter(errors__isnull=False)
        error_percentage = (error_codes.count() / codes_for_the_day.count() * 100) if codes_for_the_day.count() else 0
        code_by_days.append((day, codes_for_the_day, error_percentage, 100 - error_percentage))

    group_codes = models.Code.filter(~Q(user__uid=F('chat_id')))
    private_codes = models.Code.filter(user__uid=F('chat_id'))
    group_error_codes = group_codes.filter(errors__isnull=False)
    private_error_codes = private_codes.filter(errors__isnull=False)
    groups_errors_percentage_by_days = [
        i[1].filter(
            ~Q(user__uid=F('chat_id')), errors__isnull=False
        ).count() /
        (i[1].filter(
            ~Q(user__uid=F('chat_id')), errors__isnull=True
        ).count() or 1) for i in code_by_days
    ]

    private_errors_percentage_by_days = [
        i[1].filter(
            user__uid=F('chat_id'), errors__isnull=False
        ).count() /
        (i[1].filter(
            user__uid=F('chat_id'), errors__isnull=True
        ).count() or 1) for i in code_by_days
    ]

    groups = {
        "codes": group_codes.count(),
        "errors": group_error_codes.count(),
        "errors_by_time": groups_errors_percentage_by_days,
        "success": group_codes.count() - group_error_codes.count()
    }

    private = {
        "codes": private_codes.count(),
        "errors": private_error_codes.count(),
        "errors_by_time": private_errors_percentage_by_days,
        "success": private_codes.count() - private_error_codes.count()
    }
    time_labels = [int(i[0].strftime("%d")) for i in code_by_days]

    stats = {
        "overall_codes": codes_for_last_month.count(),
        "groups": groups,
        "private": private,
        "time_labels": time_labels
    }
    return render(request, "core/stats.html", context={"stats": stats})
