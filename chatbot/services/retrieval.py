import re

from django.db.models import Q

from chatbot.models import KnowledgeEntry
from products.models import Product


STOP_WORDS = {
    'a',
    'an',
    'and',
    'are',
    'can',
    'do',
    'for',
    'i',
    'in',
    'is',
    'me',
    'of',
    'please',
    'show',
    'the',
    'to',
    'you',
}


def extract_terms(message):
    words = re.findall(r'\b[\w-]+\b', message.lower())

    return [
        word
        for word in words
        if len(word) > 2 and word not in STOP_WORDS
    ]


def retrieve_products(message, limit=5):
    terms = extract_terms(message)

    if not terms:
        return Product.objects.none()

    query = Q()

    for term in terms:
        query |= Q(name__icontains=term)
        query |= Q(description__icontains=term)
        query |= Q(category__name__icontains=term)

    return (
        Product.objects
        .filter(query)
        .distinct()[:limit]
    )


def retrieve_knowledge(message, limit=4):
    terms = extract_terms(message)

    if not terms:
        return KnowledgeEntry.objects.none()

    query = Q()

    for term in terms:
        query |= Q(title__icontains=term)
        query |= Q(content__icontains=term)
        query |= Q(keywords__icontains=term)

    return (
        KnowledgeEntry.objects
        .filter(
            query,
            is_active=True,
        )
        .distinct()[:limit]
    )
