from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Messages, Contacts, Products, Categories, Orders, Order_Products
import json
from requests import Session

MENU_DIR = 'Menu/'
MENU = 'https://76d1-2804-e8-80a2-a00-a405-72d0-b183-97df.eu.ngrok.io/menu'
OPTIONS = "1-See Menu\n2-Make an Order\n3-Promotions\n4-Address\n5-Opening hours"

RESPONSES = {
    "Greetings" : f"Welcome to the Pizzaria!\nMy name is Mara, the Robot!\nHere's a list of what i can do for you\n{OPTIONS}",
    "Menu" : f"Here's our menu, {MENU}",
    "Order" : f"You can Order here, {MENU}",
    "Promotions" : f"There's no active promotions at moment\nBut you can see our menu here: {MENU}",
    "Address" : "We're located at Stree street, Avenue, 123 - Washinghton",
    "Opening" : "Sunday 11:00AM-11:30PM\nMonday Closed\nTuesday 11:00AM-11:30PM\nWednesday 11:00AM-11:30PM\nThursday 11:00AM-11:30PM\nFriday 11:00AM-11:30PM\nSaturday 11:00AM-11:30PM\n",
    "Human" : "We're calling a Human, wait a second!", # not used yet
    "Options" : "1-See Menu\n2-Make an Order\n3-Promotions\n4-Address\n5-Opening hours",
    "404" : f"I didn't understand what you're saying, let's try again\n{OPTIONS}",
}

# Create your views here.
@csrf_exempt
def webhook(request): # Get all the data send from whatsapp api and registar contact if it didn't exist and messages
    if request.method == "GET":
        return HttpResponse(request.GET.get('hub.challenge'))
    if request.method == "POST":
        try:
            test = json.loads(request.body)
            name = test['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            from_number = test['entry'][0]['changes'][0]['value']['messages'][0]['from']
            to_number = test['entry'][0]['changes'][0]['value']['metadata']['display_phone_number']
            message_text = test['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        
            if not Contacts.objects.filter(phone_number = from_number).exists():
                Contacts.objects.create(name = name, phone_number = from_number)
            
            contact = Contacts.objects.get(phone_number = from_number)

            message = Messages.objects.create(from_number=from_number, to_number = to_number, message_text = message_text, contact_id = contact)

            if contact.first_message:
                Contacts.objects.filter(phone_number = from_number).update(first_message = False)
                start_order(contact)
            else:
                check_status(contact, message)
        except:
            print('POST ignored')
    return HttpResponse("Test")

def chat(request): #Show all numbers that messaged
    contact = Contacts.objects.all()
    return render(request, 'home.html', {'contact' : contact})

def chatting(request, id): #Send message to the user via textbox
    messages = Messages.objects.filter(contact_id = id)
    if request.method == "POST":
        text = request.POST.get('text')
        to = Contacts.objects.filter(id = id)
        toNumber = to[0].phone_number
        send_message(text, toNumber, to[0])
        
    return render(request, 'chatting.html', {'messages' : messages})


def start_order(contact): #Send the Greetings for the first message
    send_message(RESPONSES['Greetings'], contact.phone_number, contact)

def update_order(contact,order): #Update the order for the user, send him a wpp message
    message = f'Your order is placed successfully! I will update you here.\n\nDelivering to:{order.deliver_address}\n\nItens:\n'

    for x in Order_Products.objects.filter(order_id = order):
        y = Products.objects.filter(id = x.product_id.id)
        message += f'{x.quantity}x {y[0].name}\n'
        print(y[0].name, x.quantity, order.total_value)
    
    message += f'\nTotal: ${order.total_value}\n\nWe\'re preparing your order, we\'ll notify you when it\'s on the way!'
    send_message(message, contact.phone_number, contact)

def check_status(contact, message): #Check what's user want to do
    if message.message_text == '1':
        answer = RESPONSES['Menu'] + f"/{contact.phone_number}"
    elif message.message_text == '2':
        answer = RESPONSES['Order'] + f"/{contact.phone_number}"
    elif message.message_text == '3':
        answer = RESPONSES['Promotions'] + f"/{contact.phone_number}"
    elif message.message_text == '4':
        answer = RESPONSES['Address']
    elif message.message_text == '5':
        answer = RESPONSES['Opening']
    else:
        answer = RESPONSES['404']
    send_message(answer, contact.phone_number, contact)

def send_message(text, toNumber, toId): #Generic message template, parse the data and send to the Whatsapp API
    base_url = 'https://graph.facebook.com/'
    api_version = 'v15.0/'
    sender = '101210056108048/'
    endpoint = 'messages'
    url = base_url + api_version + sender + endpoint
    
    api_token = 'EAAMhCXZAGkHwBAGBuFdfT9RToiVlWBW2yEnhGPpkeCUKF6b9npZBC1OF4OBP7xeZCjtGJanBkmO3fvk801d3uxHpUM4KYr8t0l2oXYAtNg0IrHS9iZAA0qWtZAeWmRHns2WoZAZCFsJAfMD5xEnuukjAkAt0ieU1ZCn6Q5GVkLbAT6xWpoiHT7VZABBpo5YZCQQJiczZBIkpizThAZDZD'

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
        Messages.objects.create(from_number='14991202420', to_number = toNumber, message_text = text, contact_id = toId)
        print(f"data: {data}")

    except (ConnectionError) as e:
        print(e)


def menu(request, number): #Get the itens that user wanna buy
    if request.method == 'POST':
        total = 0
        contact = Contacts.objects.filter(phone_number = number)
        Orders.objects.create(contact_id = contact[0], total_value = total)
        order = Orders.objects.filter(contact_id = contact[0]).last()
        for id, quantity in request.POST.items():
            if id != 'csrfmiddlewaretoken' and int(quantity) > 0:
                product = Products.objects.get(id=id)
                total += product.price * int(quantity)
                Order_Products.objects.create(order_id = order, product_id = product, quantity = quantity)

        order.total_value = total
        order.save()

        return redirect(f'./{number}/{order.id}')
    categorys = {category : Products.objects.filter(category = category) for category in Categories.objects.all()}
    return render(request, 'menu.html', {'categories':categorys})

def complete_order(request, number, order): #Get Address and aditional info to place the order
    contact = Contacts.objects.get(phone_number = number)
    order = Orders.objects.get(id = order)
    name = contact.name
    total = order.total_value
    if request.method == 'POST':
        order.status = 'Preparing'
        address = ' '.join((request.POST['Address1'], request.POST['Address2'], request.POST['Zip_code'], request.POST['Apartment']))
        order.observation = request.POST['Observation']
        order.deliver_address = address
        order.save()

        update_order(contact,order)
        return HttpResponse('Order done!')
    return render(request, "complete_order.html", {'name' : name, 'total' : total})