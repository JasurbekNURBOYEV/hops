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
    a_month_before_date = (timezone.now() - timedelta(days=30)).date()
    codes_for_last_month = models.Code.filter(created_time__gte=a_month_before_date)
    code_by_days = []
    for i in range(31):
        day = a_month_before_date + timedelta(days=i)
        next_day = day + timedelta(days=1)
        codes_for_the_day = codes_for_last_month.filter(created_time__lte=next_day, created_time__gte=day)
        code_by_days.append((day, codes_for_the_day))

    group_codes = codes_for_last_month.filter(~Q(user__uid=F('chat_id')))
    private_codes = codes_for_last_month.filter(user__uid=F('chat_id'))
    group_error_codes = group_codes.filter(errors__isnull=False)
    private_error_codes = private_codes.filter(errors__isnull=False)
    groups_errors_percentage_by_days = []
    private_errors_percentage_by_days = []
    group_error_counts = []
    group_total_counts = []
    private_error_counts = []
    private_total_counts = []
    for day, codes in code_by_days:
        # groups stats
        group_total_codes = codes.filter(~Q(user__uid=F('chat_id')))
        group_errors = group_total_codes.filter(errors__isnull=False).count()
        groups_errors_percentage_by_days.append(round(group_errors / (group_total_codes.count() or 1) * 100, 2))

        group_error_counts.append(group_errors)
        group_total_counts.append(group_total_codes.count())

        # private stats
        private_totoal_codes = codes.filter(user__uid=F('chat_id'))
        private_errors = private_totoal_codes.filter(errors__isnull=False).count()
        private_errors_percentage_by_days.append(round(private_errors / (private_totoal_codes.count() or 1) * 100, 2))

        private_error_counts.append(private_errors)
        private_total_counts.append(private_totoal_codes.count())

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
    time_labels = [int(day.strftime("%d")) for day, codes in code_by_days]

    stats = {
        "overall_codes": codes_for_last_month.count(),
        "groups": groups,
        "private": private,
        "time_labels": time_labels,
        "group_errors": group_error_counts,
        "group_totals": group_total_counts,
        "private_errors": private_error_counts,
        "private_totals": private_total_counts
    }

    # grouped bar chart
    return render(request, "core/stats.html", context={"stats": stats})
