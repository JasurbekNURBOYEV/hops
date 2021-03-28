from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ocean.runner import BubbleRunner


@csrf_exempt
def bubble(request, *args, **kwargs):
    code = request.POST.get("code")
    inp = request.POST.get("input", "")
    runner = BubbleRunner()
    result, errors, stats = runner.run(code, inp)
    return JsonResponse(dict(Result=result, Errors=errors, Stats=stats))
