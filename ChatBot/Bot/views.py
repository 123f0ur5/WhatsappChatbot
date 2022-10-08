from turtle import title
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Messages, Contacts, Products, Categories, Orders, Order_Products
import json
from requests import Session
from ChatBot.settings import API_TOKEN

MENU_DIR = 'Menu/'
MENU = 'https://4281-2804-e8-80a2-a00-a405-72d0-b183-97df.eu.ngrok.io/menu'
OPTIONS = "1-See Menu\n2-Make an Order\n3-Promotions\n4-Address\n5-Opening hours"
NUMBER = '14991202420'

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
    "Delivering" : "Your order is on the way! It'll arrive soon",
    "Finish" : "Tell us more about your experience!\nIt was everything fine?",
    "Finish_Social" : "We're more than happy to invite you to our social media\n@Facebook\n@Instagram",
}

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
    
    headers = {"Authorization" : f"Bearer {API_TOKEN}",
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
        Messages.objects.create(from_number=NUMBER, to_number = toNumber, message_text = text, contact_id = toId)
        print(f"data: {data}")

    except (ConnectionError) as e:
        print(e)

def send_interactive_message(text, toNumber, toId): #Generic message template, parse the data and send to the Whatsapp API
    base_url = 'https://graph.facebook.com/'
    api_version = 'v15.0/'
    sender = '101210056108048/'
    endpoint = 'messages'
    url = base_url + api_version + sender + endpoint
    
    headers = {"Authorization" : f"Bearer {API_TOKEN}",
                "Contect-Type" : "application/json",
    }

    parameters = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": toNumber,
        "type": "interactive",
        "interactive" : {
            "type" : "list",
            "header" : {
                "type" : "text",
                "text" : "Your order is done!"
            },
            "body" : {
                "text" : text
            },
            "footer": {
                "text": "Click on \"How was your order?\""
            },
            "action" : {
                "button" : "How was your order?",
                "sections" : [
                    {
                        "title" : "How was your experience?",
                        "rows" : [
                            {
                                "id" : "Perfect",
                                "title" : "It was perfect!",
                                "description" : ""
                            },
                            {
                                "id" : "Good",
                                "title" : "It was good!",
                                "description" : ""
                            },
                            {
                                "id" : "Bad",
                                "title" : "It was bad :(",
                                "description" : ""
                            },
                            {
                                "id" : "Delivery",
                                "title" : "I didn't get the order",
                                "description" : ""
                            },
                        ]
                    }
                ]
            }
        }
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.post(url, json=parameters)
        data = json.loads(response.text)
        Messages.objects.create(from_number=NUMBER, to_number = toNumber, message_text = text, contact_id = toId)
        print(f"data: {data}")

    except (ConnectionError) as e:
        print(e)

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
                total_product = product.price * int(quantity)
                Order_Products.objects.create(order_id = order, product_id = product, quantity = quantity, total = total_product)

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

def manage(request):
    orders = Orders.objects.filter(status__in = ('Delivering', 'Preparing'))
    return render(request, 'manage.html', {'orders' : orders})

def manage_order(request, id):
    p_order = Order_Products.objects.filter(order_id = id)
    order = Orders.objects.get(id = id)
    if request.method == 'POST':
        if request.POST.get('button') == 'Dispatch':
            order.status = 'Delivering'
            send_message(RESPONSES['Delivering'],order.contact_id.phone_number,order.contact_id)
            order.save()
        else:
            order.status = 'Done'
            send_interactive_message(RESPONSES["Finish"],order.contact_id.phone_number,order.contact_id)
            send_message(RESPONSES['Finish_Social'],order.contact_id.phone_number,order.contact_id)
            order.save()
            return redirect('manage')

    return render(request, 'manage_order.html', {'products' : p_order, 'order' : order})