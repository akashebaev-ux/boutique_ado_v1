import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from products.models import Product


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

    # -----------------------------
    # PRODUCT SEARCH STARTS HERE
    # -----------------------------

    words = message.lower().split()

    ignored_words = {
        'do',
        'you',
        'have',
        'a',
        'an',
        'the',
        'me',
        'show',
        'please',
        'can',
        'i',
        'find',
    }

    search_words = [
        word.strip('?.!,')
        for word in words
        if word.strip('?.!,') not in ignored_words
    ]

    query = Q()

    for word in search_words:
        query |= Q(name__icontains=word)
        query |= Q(description__icontains=word)
        query |= Q(category__name__icontains=word)

    if search_words:
        products = Product.objects.filter(
            query
        ).distinct()[:5]
    else:
        products = Product.objects.none()

    # -----------------------------
    # PRODUCT SEARCH ENDS HERE
    # -----------------------------

    if products.exists():
        product_names = [
            product.name
            for product in products
        ]

        answer = (
            "I found these products: "
            + ", ".join(product_names)
            + "."
        )

    else:
        answer = (
            "I couldn't find a matching product. "
            "Try asking for a product name or category."
        )

    return JsonResponse({
        'answer': answer
    })
