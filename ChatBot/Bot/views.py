from datetime import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Messages, Contacts, Products, Categories, Orders, Order_Products
from .forms import ProductForm, CategoryForm
import json, os
from requests import Session
from ChatBot.settings import API_TOKEN, URL

MENU_DIR = 'Menu/'
MENU = f'https://{URL}/menu'
OPTIONS = "1-See Menu\n2-Make an Order\n3-Promotions\n4-Address\n5-Opening hours"
NUMBER = '14991202420'
DELIVERY_PRICE = 5.00

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
    "Perfect" : "Happy to hear that, we're waiting you next time",
    "Good" : "We're looking to improve so the next time will be everything perfect!",
    "Bad" : "We're sad to hear that, can you explain why it was bad?",
    "404Order" : "We're sad to hear that, we're looking for what happened with your order. We will call you soon",
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
    elif message.message_text == 'It was perfect!':
        answer = RESPONSES['Perfect']
    elif message.message_text == 'It was good!':
        answer = RESPONSES['Good']
    elif message.message_text == 'It was bad :(':
        answer = RESPONSES['Bad']
    elif message.message_text == 'I didn\'t get the order':
        answer = RESPONSES['404Order']
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
        session.post(url, json=parameters)
        Messages.objects.create(from_number=NUMBER, to_number = toNumber, message_text = text, contact_id = toId, sent_datetime = datetime.now().replace(microsecond=0))

    except (ConnectionError) as e:
        print(e)

def send_interactive_message(text, toNumber, toId): #Interactive message template, parse the data and send to the Whatsapp API
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
        session.post(url, json=parameters)
        Messages.objects.create(from_number=NUMBER, to_number = toNumber, message_text = text, contact_id = toId, sent_datetime = datetime.now().replace(microsecond=0))

    except (ConnectionError) as e:
        print(e)

def format_phone(number):
    number = number[2:]
    if len(number) == 10:
        return '({}) {}-{}'.format(number[0:2], number[2:6], number[6:])
    else:
        return '({}) {} {}-{}'.format(number[0:2], number[2:3], number[3:7], number[7:])

def print_receipt(id):
    local = 'last_receipt.txt'
    p_order = Order_Products.objects.filter(order_id = id)
    order = Orders.objects.get(id=id)
    prods = ""
    obs = ""
    if order.observation != '':
        obs = f' Obs: {order.observation}\n\n'
    for product in p_order:
        p = f" {product.quantity}x {product.product_id.name} ${product.product_id.price}"
        p = p.ljust(30, ' ')
        p += f"${product.total}\n"
        prods += p
    receipt =f"\
-----------------------------------------\n\
                Test Name                \n\
      Richard Chermisson Avenue, 379     \n\
            (12) 3 45678-1234            \n\
         CNPJ: 12 345 678/0001-12        \n\
-----------------------------------------\n\
       ** DOCUMENTO NÃO FISCAL **        \n\
\n\
 Impresso em {datetime.now().replace(microsecond=0)}\n\
\n\
 Cliente: {order.contact_id.name}\n\
 Telefone: {format_phone(order.contact_id.phone_number)}\n\
 Endereço: {order.deliver_address}\n\
-----------------------------------------\n\
{obs}\
          Pedido número: {order.pk}\n\
 Qtd. Item  V. Unitário       Total\n\
{prods}\
-----------------------------------------\n\
 Total:                       ${order.total_value}\n\
 + Delivery:                  ${DELIVERY_PRICE}\n\
 = Total a Pagar:             ${order.total_value + DELIVERY_PRICE}\n\
-----------------------------------------\n\
        Obrigado pela preferência!\n\
-----------------------------------------\n\
" #obs has 2 \n
    with open(f'{local}', 'w+') as f:
        f.write(receipt)
        os.startfile(f'{local}' ,'print')

# Create your views here.
@csrf_exempt
def webhook(request): # Get all the data send from whatsapp api and registar contact if it didn't exist and messages
    if request.method == "GET":
        return HttpResponse(request.GET.get('hub.challenge'))
    if request.method == "POST":
        completed = False
        test = json.loads(request.body)
        print(request.body)
        try:
            name = test['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
            from_number = test['entry'][0]['changes'][0]['value']['messages'][0]['from']
            to_number = test['entry'][0]['changes'][0]['value']['metadata']['display_phone_number']
            sent_datetime = test['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
            try:
                message_text = test['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                completed = True
            except:
                try:
                    message_text = test['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['title']

                    completed = True
                except:
                    pass
        except:
            pass
            
        if completed:
            sent_datetime = datetime.fromtimestamp(int(sent_datetime))
        
            if not Contacts.objects.filter(phone_number = from_number).exists():
                Contacts.objects.create(name = name, phone_number = from_number)
            
            contact = Contacts.objects.get(phone_number = from_number)

            Messages.objects.create(from_number=from_number, to_number = to_number, message_text = message_text, sent_datetime = sent_datetime, contact_id = contact)

            message = Messages.objects.filter(from_number=from_number).order_by('-id')[:2]
            if int((datetime.now() - message[1].sent_datetime).total_seconds()/60) > 180:
                start_order(contact)
            else:
                message = Messages.objects.filter().last()
                check_status(contact, message)

    return HttpResponse("200")

def chat(request): #Show all numbers that messaged
    last_message = {id : Messages.objects.filter(contact_id = id).last() for id in Contacts.objects.all()}
    if request.method == "POST":
        id = request.POST.get('id')
        text = request.POST.get('text')
        messages = Messages.objects.filter(contact_id = id)
        num_orders = Orders.objects.filter(contact_id = id).count()
        active_orders = Orders.objects.filter(contact_id = id, status__in = ('Delivering', 'Preparing'))
        if text != None:
            to = Contacts.objects.get(id = id)
            send_message(text, to.phone_number, to)
    else:
        messages = None
        active_orders = None
        num_orders = 0
    return render(request, 'Chat/chat.html', {'contact' : last_message, 'messages' : messages, 'num_orders' : num_orders, 'active_orders' : active_orders})

def chatting(request, id): #Send message to the user via textbox
    messages = Messages.objects.filter(contact_id = id)
    if request.method == "POST":
        text = request.POST.get('text')
        to = Contacts.objects.filter(id = id)
        toNumber = to[0].phone_number
        send_message(text, toNumber, to[0])
        
    return render(request, 'Chat/chatting.html', {'messages' : messages})

def client_menu(request, number): #Get the itens that user wanna buy
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
    categories = {category : Products.objects.filter(category = category) for category in Categories.objects.all()}
    return render(request, 'Menu/client_menu.html', {'categories':categories})

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
        order.order_date = datetime.now().replace(microsecond=0)
        order.save()

        update_order(contact,order)
        return HttpResponse('Order done!')
    return render(request, "Menu/complete_order.html", {'name' : name, 'total' : total})

def manage(request):
    orders = Orders.objects.filter(status__in = ('Delivering', 'Preparing'))
    return render(request, 'Manage/manage.html', {'orders' : orders})

def manage_order(request, id):
    p_order = Order_Products.objects.filter(order_id = id)
    order = Orders.objects.get(id = id)
    if request.method == 'POST':
        if request.POST.get('print'):
            print_receipt(id)
        if request.POST.get('button_dispatch'):
            order.status = 'Delivering'
            send_message(RESPONSES['Delivering'],order.contact_id.phone_number,order.contact_id)
            order.save()
        if request.POST.get('button_finish'):
            order.status = 'Done'
            send_interactive_message(RESPONSES["Finish"],order.contact_id.phone_number,order.contact_id)
            send_message(RESPONSES['Finish_Social'],order.contact_id.phone_number,order.contact_id)
            order.save()
            return redirect('manage')

    return render(request, 'Manage/manage_order.html', {'products' : p_order, 'order' : order})

def home(request):
    return render(request, 'home.html', {})

def menu(request):
    categories = {category : Products.objects.filter(category = category) for category in Categories.objects.all()}
    return render(request, 'Menu/menu.html', {'categories' : categories})

def menu_add(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_form.save()
            product_form = ProductForm()
    else:
        product_form = ProductForm()
    return render(request, 'Menu/menu_add.html', {'form' : product_form})

def category_add(request):
    category_form = CategoryForm(request.POST or None)
    if request.method == 'POST':
        if category_form.is_valid():
            category_form.save()
            category_form = CategoryForm()
    return render(request, 'Menu/menu_category.html', {'form' : category_form})

def edit_product(request, id):
    product = Products.objects.get(id = id)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('menu')
    else:
        product_form = ProductForm(instance=product)
    return render(request, 'Menu/edit_product.html', {'form' : product_form})

def delete_product(request,id):
    product = Products.objects.get(id = id)
    if request.method == 'POST':
        product.delete()
        return redirect('menu')

    return render(request, 'Menu/delete_product.html', {'product' : product})

def category_manage(request):
    categories = Categories.objects.all()
    return render(request, 'Menu/category_manage.html', {'categories' : categories})

def category_delete(request, id):
    category = Categories.objects.get(id = id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_manage')
    return render(request, 'Menu/category_delete.html', {'category' : category})