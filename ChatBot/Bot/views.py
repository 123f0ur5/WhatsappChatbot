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
        print(request.body)
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

            if contact.first_message:
                Contact.objects.filter(phone_number = from_number).update(first_message = False)
                start_order(contact)
            else:
                check_status(contact)
        except:
            print('POST ignored')
    return HttpResponse("Test")

def chat(request):
    contact = Contact.objects.all()
    return render(request, 'home.html', {'contact' : contact})

def chatting(request, id):
    messages = Message.objects.filter(contact_id = id)
    if request.method == "POST":
        text = request.POST.get('text')
        to = Contact.objects.filter(id = id)
        toNumber = to[0].phone_number
        send_message(text, toNumber, to[0])
        
    return render(request, 'chatting.html', {'messages' : messages})


def start_order(contact):
    message = ("Welcome to the Pizzaria!\nMy name is Mara, the Robot!\n"+
    "Here's a list of what i can do for you\n1-See Menu\n2-Make an Order\n3-Promotions")
    send_message(message, contact.phone_number, contact)

def check_status(contact):
    message = ("Here's your menu!")
    send_message(message, contact.phone_number, contact)

def send_message(text, toNumber, toId):
    base_url = 'https://graph.facebook.com/'
    api_version = 'v15.0/'
    sender = '101210056108048/'
    endpoint = 'messages'
    url = base_url + api_version + sender + endpoint
    
    api_token = 'EAAMhCXZAGkHwBACBwJpDM3X5agxbxVUAn8upT4nrvZCSqlnLoUZAJnKTg6jTZCutkbt4d7aNvkN9x7b6RCcWqeAUfE0sBZBYUOTfVDQTSkCKgi9pbdkC2YI8NP5XI76vhvKZCAHQXNItZBuwXScFu5Nh9RDrcjDZBdFygZCjmJwFjwpPaUoNfw5JStnr9nOEDLpssc9miQhgCKgZDZD'

    headers = {"Authorization" : f"Bearer {api_token}",
    }

    parameters = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": toNumber,
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
        Message.objects.create(from_number='14991202420', to_number = toNumber, message_text = text, contact_id = toId)
        print(f"data: {data}")

    except (ConnectionError) as e:
        print(e)