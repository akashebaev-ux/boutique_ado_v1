import json
import re

from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from products.models import Product


IGNORED_WORDS = {
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
    'your',
    'some',
    'any',
    'are',
    'there',
    'for',
    'looking',
    'want',
    'need',
}


PLURAL_WORDS = {
    'dresses': 'dress',
    'shirts': 'shirt',
    'jackets': 'jacket',
    'bags': 'bag',
    'shoes': 'shoe',
    'skirts': 'skirt',
    'tops': 'top',
    'trousers': 'trouser',
}


NO_PREFERENCE_VALUES = {
    'no preference',
    'none',
    'any',
    'anything',
    'not sure',
    'does not matter',
}


def chatbot(request):
    """
    Basic chatbot development page.
    """
    return HttpResponse("Boutique Ado Chatbot")


def extract_search_term(message):
    """
    Extract useful product words from the customer's message.

    Example:
    "Do you have dresses?"
    becomes:
    "dress"
    """

    words = re.findall(
        r"[A-Za-z0-9'-]+",
        message.lower()
    )

    search_words = []

    for word in words:

        if word in IGNORED_WORDS:
            continue

        word = PLURAL_WORDS.get(
            word,
            word
        )

        search_words.append(word)

    return " ".join(search_words)


def base_product_search(search_term):
    """
    Search Boutique Ado products by name,
    description and category.
    """

    terms = search_term.split()

    query = Q()

    for term in terms:
        query |= Q(name__icontains=term)
        query |= Q(description__icontains=term)
        query |= Q(category__name__icontains=term)

    if not terms:
        return Product.objects.none()

    return (
        Product.objects
        .filter(query)
        .distinct()
    )


def apply_budget(products, budget):
    """
    Filter products by customer's budget.
    """

    if budget == 'under_25':
        return products.filter(
            price__lt=25
        )

    if budget == '25_50':
        return products.filter(
            price__gte=25,
            price__lte=50
        )

    if budget == 'over_50':
        return products.filter(
            price__gt=50
        )

    return products


def apply_text_preference(products, preference):
    """
    Search a preference such as colour or occasion
    in product name, description or category.
    """

    if not preference:
        return products

    return products.filter(
        Q(name__icontains=preference)
        | Q(description__icontains=preference)
        | Q(category__name__icontains=preference)
    )


def parse_budget(message):
    """
    Convert customer budget answer into
    an internal value.
    """

    value = message.lower().strip()

    if value in {
        'under_25',
        'under 25',
        'under $25',
        'less than 25',
    }:
        return 'under_25'

    if value in {
        '25_50',
        '25-50',
        '$25-$50',
        '$25–$50',
        '25 to 50',
    }:
        return '25_50'

    if value in {
        'over_50',
        'over 50',
        'over $50',
        'more than 50',
    }:
        return 'over_50'

    if value in {
        'any',
        'any budget',
        'no preference',
    }:
        return 'any'

    # Allow customer to type just a number
    match = re.search(
        r'\d+(?:\.\d+)?',
        value
    )

    if match:
        amount = float(match.group())

        if amount < 25:
            return 'under_25'

        if amount <= 50:
            return '25_50'

        return 'over_50'

    return None


def find_products(context):
    """
    Search using all collected customer preferences.

    If the search becomes too restrictive,
    fall back to the product + budget search.
    """

    products = base_product_search(
        context['product']
    )

    products = apply_budget(
        products,
        context.get('budget')
    )

    preferred_products = products

    preferred_products = apply_text_preference(
        preferred_products,
        context.get('occasion')
    )

    preferred_products = apply_text_preference(
        preferred_products,
        context.get('color')
    )

    exact_results = list(
        preferred_products[:5]
    )

    if exact_results:
        return exact_results, False

    # Relax colour / occasion if no exact match
    relaxed_results = list(
        products[:5]
    )

    if relaxed_results:
        return relaxed_results, True

    # Last fallback: just search the original product
    basic_results = list(
        base_product_search(
            context['product']
        )[:5]
    )

    return basic_results, True


@require_POST
def chatbot_message(request):
    """
    Guided Boutique Ado product assistant.
    """

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                'error': 'Invalid request.'
            },
            status=400
        )

    message = data.get(
        'message',
        ''
    ).strip()

    if not message:
        return JsonResponse(
            {
                'error': 'Message is required.'
            },
            status=400
        )

    if len(message) > 500:
        return JsonResponse(
            {
                'error': 'Message is too long.'
            },
            status=400
        )

    # ----------------------------------------
    # Check existing conversation
    # ----------------------------------------

    context = request.session.get(
        'chatbot_context'
    )

    # ========================================
    # STEP 2: OCCASION
    # ========================================

    if context and context.get('step') == 'occasion':

        occasion = message.lower().strip()

        if occasion in NO_PREFERENCE_VALUES:
            occasion = None

        context['occasion'] = occasion
        context['step'] = 'budget'

        request.session['chatbot_context'] = context

        return JsonResponse({
            'answer': (
                "Great. What is your approximate budget?"
            ),

            'options': [
                {
                    'label': 'Under $25',
                    'value': 'under_25',
                },
                {
                    'label': '$25–$50',
                    'value': '25_50',
                },
                {
                    'label': 'Over $50',
                    'value': 'over_50',
                },
                {
                    'label': 'Any budget',
                    'value': 'any',
                },
            ],

            'action': None,
        })

    # ========================================
    # STEP 3: BUDGET
    # ========================================

    if context and context.get('step') == 'budget':

        budget = parse_budget(message)

        if budget is None:

            return JsonResponse({
                'answer': (
                    "I didn't quite understand the budget. "
                    "Please choose one of these options."
                ),

                'options': [
                    {
                        'label': 'Under $25',
                        'value': 'under_25',
                    },
                    {
                        'label': '$25–$50',
                        'value': '25_50',
                    },
                    {
                        'label': 'Over $50',
                        'value': 'over_50',
                    },
                    {
                        'label': 'Any budget',
                        'value': 'any',
                    },
                ],

                'action': None,
            })

        context['budget'] = budget
        context['step'] = 'color'

        request.session['chatbot_context'] = context

        return JsonResponse({
            'answer': (
                "Perfect. Do you have a preferred colour?"
            ),

            'options': [
                {
                    'label': 'Black',
                    'value': 'black',
                },
                {
                    'label': 'White',
                    'value': 'white',
                },
                {
                    'label': 'Blue',
                    'value': 'blue',
                },
                {
                    'label': 'Red',
                    'value': 'red',
                },
                {
                    'label': 'No preference',
                    'value': 'no preference',
                },
            ],

            'action': None,
        })

    # ========================================
    # STEP 4: COLOUR + FINAL SEARCH
    # ========================================

    if context and context.get('step') == 'color':

        color = message.lower().strip()

        if color in NO_PREFERENCE_VALUES:
            color = None

        context['color'] = color

        products, relaxed_search = find_products(
            context
        )

        # Conversation is complete
        if 'chatbot_context' in request.session:
            del request.session['chatbot_context']

        if not products:
            return JsonResponse({
                'answer': (
                    "I couldn't find products matching "
                    "those preferences. "
                    "Would you like to try another search?"
                ),

                'options': None,
                'action': None,
            })

        product_names = [
            product.name
            for product in products
        ]

        products_url = (
            reverse('products')
            + '?'
            + urlencode({
                'q': context['product']
            })
        )

        if relaxed_search:

            answer = (
                "I couldn't find an exact match for every "
                "preference, but I found these options: "
                f"{', '.join(product_names)}. "
                "Would you like me to show you?"
            )

        else:

            answer = (
                f"I found {len(products)} product"
                f"{'s' if len(products) != 1 else ''} "
                "that match your preferences: "
                f"{', '.join(product_names)}. "
                "Would you like me to show you?"
            )

        return JsonResponse({
            'answer': answer,

            'options': None,

            'action': {
                'type': 'navigate',
                'url': products_url,
                'label': 'Yes, show me',
            },
        })

    # ========================================
    # STEP 1: NEW PRODUCT SEARCH
    # ========================================

    search_term = extract_search_term(
        message
    )

    if not search_term:
        return JsonResponse({
            'answer': (
                "What kind of product are you looking for?"
            ),
            'options': None,
            'action': None,
        })

    products = base_product_search(
        search_term
    )

    if not products.exists():

        return JsonResponse({
            'answer': (
                "I couldn't find that product in Boutique Ado. "
                "Try asking for another product or category."
            ),
            'options': None,
            'action': None,
        })

    # Save conversation state
    request.session['chatbot_context'] = {
        'product': search_term,
        'occasion': None,
        'budget': None,
        'color': None,
        'step': 'occasion',
    }

    return JsonResponse({
        'answer': (
            f"Yes, I found products related to "
            f"'{search_term}'. "
            "Before I show them, what kind are you looking for?"
        ),

        'options': [
            {
                'label': 'Casual',
                'value': 'casual',
            },
            {
                'label': 'Party',
                'value': 'party',
            },
            {
                'label': 'Formal',
                'value': 'formal',
            },
            {
                'label': 'Everyday',
                'value': 'everyday',
            },
            {
                'label': 'No preference',
                'value': 'no preference',
            },
        ],

        'action': None,
    })
