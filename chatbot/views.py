from django.http import HttpResponse


def chatbot(request):
    """Basic chatbot view used while the chatbot is being developed."""
    return HttpResponse("Boutique Ado Chatbot")
