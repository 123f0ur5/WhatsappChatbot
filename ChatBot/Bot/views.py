from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message, Contact
import json
from requests import Session


# Create your views here.
@csrf_exempt
def webhook(request):
    if request.method == "GET":
        return HttpResponse(request.GET.get('hub.challenge'))
    if request.method == "POST":
        try:
            test = json.loads(request.body)
            name = test['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            from_number = test['entry'][0]['changes'][0]['value']['messages'][0]['from']
            to_number = test['entry'][0]['changes'][0]['value']['metadata']['display_phone_number']
            message_text = test['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        
            if not Contact.objects.filter(phone_number = from_number).exists():
                Contact.objects.create(name = name, phone_number = from_number)
            
            contact = Contact.objects.get(phone_number = from_number)

            Message.objects.create(from_number=from_number, to_number = to_number, message_text = message_text, contact_id = contact)
        except:
            print('POST não reconhecido')
    return HttpResponse("200")

def chat(request):
    contact = Contact.objects.all()
    return render(request, 'home.html', {'contact' : contact})

def chatting(request, id):
    messages = Message.objects.filter(contact_id = id)
    if request.method == "POST":
        text = request.POST.get('text')
        base_url = 'https://graph.facebook.com/'
        api_version = 'v15.0/'
        sender = '101210056108048/'
        endpoint = 'messages'
        url = base_url + api_version + sender + endpoint
        to = Contact.objects.filter(id = id)
        api_token = 'EAAMhCXZAGkHwBAM2y8i7Bie58tkjeyK6NFmQCsq6sW5kt5JqZACfCXZCeTdIIW2xEHCBSRmYdxGvWuisJKp8XZB1mbsFyTRiMnq8SRFB7LgitZAGCY0y9InJHR0Tfsq89BSAIV7lwvPqzxPiioHEMjjAe71tWICbTNJLP0bozx3oTZBxfHXHFXVBZCq9ueHZAHxhAZCEFRQKGaAZDZD'

        headers = {"Authorization" : f"Bearer {api_token}",
        }

        parameters = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to[0].phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text,
        }
        }
        session = Session()
        session.headers.update(headers)
        try:
            response = session.post(url, json=parameters)
            data = json.loads(response.text)
            print(f"data: {data}")
        except (ConnectionError) as e:
            print(e)
        
        Message.objects.create(from_number='14991202420', to_number = to[0].phone_number, message_text = text, contact_id = to[0])
        

    return render(request, 'chatting.html', {'messages' : messages})