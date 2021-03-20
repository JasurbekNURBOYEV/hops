"""
Main views file.
We'll be implementing the base control units here.

"""
# --- START: IMPORTS
# built-in
# local
import traceback
from datetime import timedelta
from core import models
from core.factory import bot

# django-specific
from django.db.models import F, Q
from django.shortcuts import render
from django.utils import timezone
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
        try:
            bot.process_new_updates([update])
        except:
            print(traceback.format_exc())
        return JsonResponse(dict(ok=True))
    else:
        return JsonResponse(dict(ok=False), status=400)


def show_stats(request, *args, **kwargs):
    a_month_before_date = timezone.now() - timedelta(days=30)
    codes_for_last_month = models.Code.filter(created_time__gte=a_month_before_date)
    code_by_days = []
    for i in range(31):
        day = a_month_before_date + timedelta(days=i)
        previous_day = day - timedelta(days=1)
        codes_for_the_day = codes_for_last_month.filter(created_time__lte=day, created_time__gte=previous_day)
        # calculate error percentage
        error_codes = codes_for_the_day.filter(errors__isnull=False)
        error_percentage = (error_codes.count() / codes_for_the_day.count() * 100) if codes_for_the_day.count() else 0
        code_by_days.append((day, codes_for_the_day, error_percentage, 100 - error_percentage))

    group_codes = codes_for_last_month.filter(~Q(user__uid=F('chat_id')))
    private_codes = codes_for_last_month.filter(user__uid=F('chat_id'))
    group_error_codes = group_codes.filter(errors__isnull=False)
    private_error_codes = private_codes.filter(errors__isnull=False)
    groups_errors_percentage_by_days = []
    private_errors_percentage_by_days = []
    for i in code_by_days:
        # groups stats
        group_corrects = i[1].filter(~Q(user__uid=F('chat_id')), errors__isnull=False).count()
        group_errors = i[1].filter(~Q(user__uid=F('chat_id')), errors__isnull=True).count()
        groups_errors_percentage_by_days.append(group_corrects / (group_errors or 1) * 100)
        # private stats
        private_corrects = i[1].filter(user__uid=F('chat_id'), errors__isnull=False).count()
        private_errors = i[1].filter(user__uid=F('chat_id'), errors__isnull=True).count()
        private_errors_percentage_by_days.append(private_corrects / (private_errors or 1) * 100)

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
