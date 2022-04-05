
from flask import Flask, make_response, render_template, request

app = Flask(__name__)
application = app

OPERATIONS = ['+', '-', '*', '/']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html'))
    if request.cookies.get('name') is None:
        response.set_cookie('name', 'qq')
    else:
        response.set_cookie('name', 'qq', expires=0)
    return response

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/calc', methods=['GET', 'POST'])
def calc():
    result = None
    error_msg = None
    if request.method == 'POST':
        try:
            operand1 = float(request.form.get("operand1"))
            operand2 = float(request.form.get("operand2"))
            operation = request.form.get("operation")
            if operation == '+':
                result = operand1 + operand2
            if operation == '-':
                result = operand1 - operand2
            if operation == '*':
                result = operand1 * operand2
            if operation == '/':
                result = operand1 / operand2  
        except ValueError:
            error_msg = 'oaoaoao mmmmmmmm'
    return render_template('calc.html', operations=OPERATIONS, result=result, error_msg=error_msg)


def check_number(tel):
    ac_sym = ['(', ')', '-', '+', '.']
    num_of_digits = 0
    for i in tel:
        if i.isdigit():
            num_of_digits += 1
            continue
        elif i in ac_sym:
            continue
        elif i == ' ' and (tel.find(i) == 2 or tel.find(i) == 7):
            continue
        else:
            return 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
 
    # if (tel.find('+7') != -1 or tel.find('8',0,1) != -1) and num_of_digits != 11:
    #     return 'Недопустимый ввод. Неверное количество цифр.1'
    if tel.find('+7') == 1 and num_of_digits != 11:
        return 'Недопустимый ввод. Неверное количество цифр.2'
    if tel.find('8',0,1) == 1 and num_of_digits < 11 and tel.find('.') == -1:
        return 'Недопустимый ввод. Неверное количество цифр.3'
    if not tel.find('+7') == -1 and not tel[0] == '8' and num_of_digits == 10:
        return 'Недопустимый ввод. Неверное количество цифр.2'
            
    return None

def change_number(tel):
    num_of_digits = 0
    for i in tel:
        if i.isdigit():
            num_of_digits += 1
    if tel[0] == '+':
        tel = tel.replace('+7', '8')
    if num_of_digits == 10:
        tel = '8' + tel
    tel_list = []
    for i in tel:
        if i.isdigit():
            tel_list.append(i)
    print(tel_list)
    tel = tel_list[0] + '-'
    for i in range(1, 4):
        tel = tel + tel_list[i]
    tel = tel + '-'
    for i in range(4, 7):
        tel = tel + tel_list[i]
    tel = tel + '-'
    for i in range(7, 9):
        tel = tel + tel_list[i]
    tel = tel + '-'
    for i in range(9, 11):
        tel = tel + tel_list[i]
    return tel

@app.route('/telephone', methods=['GET', 'POST'])
def telephone():
    result = None
    error_msg = None
    tel = '123'

    if request.method == 'POST':
        tel = request.form.get('telephone')
        error_msg = check_number(tel)
        if error_msg is None:
            result = change_number(tel)
    return render_template('telephone.html', result=result, error_msg=error_msg)
        