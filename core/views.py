"""
Main views file.
We'll be implementing the base control units here.

"""
# --- START: IMPORTS
# built-in
import logging
import traceback
from datetime import timedelta

# other/external
import telebot
# django-specific
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Count, Exists
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# local
from core import models
from core.factory import bot
from core.models import User
from greed_island.factory import bot as gi_bot, strings

# --- END: IMPORTS
from greed_island.models import Tag


@csrf_exempt
def handle_webhook_requests(request):
    """
    Here we map incoming updates to our bot instance(s) accordingly
    :param request: django request object
    :return: django JsonResponse object
    """

    def setup(_bot: telebot.TeleBot, _request_id: str) -> None:
        """
        We set necessary values/configs necessary for further processes here.
        I separated this part because we may need to apply it to more than one instance in future.
        :param _bot: TeleBot instance
        :param _request_id: unique ID for single request
        :return: None
        """

        # i decided to disable threading in order to preserve synchronous order
        _bot.threaded = False

        # i'm using dict as a context to share data between bot instances
        if hasattr(bot, 'context'):
            _bot.context[_request_id] = {'violation': False}
        else:
            _bot.context = {_request_id: {'violation': False}}

    def process_update(_bot: telebot.TeleBot, _update: telebot.types.Update):
        try:
            # process update with bot instance
            _bot.process_new_updates([_update])
        except telebot.apihelper.ApiTelegramException:
            logging.error(traceback.format_exc())

    if request.headers.get('content-type') == 'application/json':

        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        try:
            request_id = bot.generate_unique_id(json_string=json_string)
            # set-up initial configs/data
            setup(bot, request_id)

            try:
                process_update(bot, update)
                # for now, i'm using this hard coded flow of processing.
                # maybe i'll think of a controller interface later... maybe not.

                # anyway, we've just run first instance, and we got our results (in context).
                # we continue according to user behaviour: we do not run next bot in case of violation
                if not bot.context[request_id]['violation']:
                    # process update with greed island bot instance
                    process_update(gi_bot, update)
            finally:
                # time to clean
                # remove redundant data from context. we've already used it and we don't need it anymore
                bot.context.pop(request_id)

        except KeyError:
            # we could not generate request id, because some keys were missing.
            # we just go with main instance in this case
            process_update(bot, update)

        return JsonResponse(dict(ok=True))
    else:
        return JsonResponse(dict(ok=False), status=400)


def show_stats(request, *args, **kwargs):
    """
    To show stats based on usage of features of Hops
    :param request: request instance
    :param args: just...
    :param kwargs: no attention
    :return: rendered HttpResponse
    """

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


def home(request, *args, **kwargs):
    return render(request, "core/home.html")


def tags(request, uuid, *args, **kwargs):
    """
    Working with tags: subscribe / unsubscribe
    :param request: request instance
    :param uuid: uuid of user instance
    :param args: no attention
    :param kwargs: still, no attention
    :return: rendered HttpResponse
    """

    def generate_tags_dashboard(_user):
        """
        Generate main dashboard of Tags.
        :param _user: user instance
        :return: complete HttpResponse to return to frontend
        """
        subscribed_tags = set(_user.tags.values_list('pk', flat=True))
        _tags = Tag.objects.annotate(
            subscribers_count=Count('subscribers')
        ).values('pk', 'name', 'subscribers_count').order_by('-subscribers_count')

        # check tag if user is subscriber of it
        for _tag in _tags:
            if _tag['pk'] in subscribed_tags:
                # we use the value 'checked' to directly put inside checkbox component
                _tag['checked'] = 'checked'
            else:
                _tag['checked'] = ''

        return render(request, "greed_island/tags.html", context=dict(tags=_tags, uuid=uuid))

    if request.method == 'GET':
        query = request.GET

        try:
            user = User.get(uuid=uuid)
        except ValidationError:
            return render(request, "greed_island/tags.html")

        if not query:
            # we show all available tags and then let user choose their favourite ones to subscribe
            return generate_tags_dashboard(user)
        else:
            # we have request to change tag subscription
            # filter to extact PKs only
            tag_pks = [int(pk) for pk in query.getlist('tag') if pk.isdigit()]

            # register new tags
            for pk in tag_pks:
                tag = Tag.get(pk=pk)

                # we may get invalid PKs, having non-existing tags
                if tag:
                    tag.subscribers.add(user)

            # unsubscribe from unchecked tags
            for tag in user.tags.all():
                if tag.pk not in tag_pks:
                    tag.subscribers.remove(user)

            return generate_tags_dashboard(user)

    raise NotImplementedError()
