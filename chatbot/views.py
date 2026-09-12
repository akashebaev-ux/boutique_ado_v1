import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST


def chatbot(request):
    return HttpResponse("Boutique Ado Chatbot")


@require_POST
def chatbot_message(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid request.'},
            status=400
        )

    message = data.get('message', '').strip()

    if not message:
        return JsonResponse(
            {'error': 'Message is required.'},
            status=400
        )

    return JsonResponse({
        'answer': f'You asked: {message}'
    })
