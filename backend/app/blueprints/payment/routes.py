import re
from flask import render_template, request, redirect, jsonify

# Import the blueprint instance from the `__init__.py`
from . import payment_bp

import math
from datetime import datetime
from app.blueprints.payment.vnpay import vnpay
from app import app

def get_client_ip(request):
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.remote_addr
    return ip

@payment_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'GET':
        # ...
        order_id = '1' + re.sub(r'[-:. ]', '', str(datetime.now()))
        return render_template('payment/payment.html', order_id=order_id)
    else:
        order_id = request.form.get('order_id')
        order_type = request.form.get('order_type')
        amount = float(request.form.get('amount'))
        order_desc = request.form.get('order_desc')
        bank_code = request.form.get('bank_code')
        language = request.form.get('language')
        ipaddr = get_client_ip(request)
        
        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = app.config['VNPAY_TMN_CODE']
        vnp.requestData['vnp_Amount'] = int(amount * 100)
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = order_id
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type
        # Check language, default: vn
        if language and language != '':
            vnp.requestData['vnp_Locale'] = language
        else:
            vnp.requestData['vnp_Locale'] = 'vn'
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData['vnp_BankCode'] = bank_code

        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = app.config['VNPAY_RETURN_URL']
        vnpay_payment_url = vnp.get_payment_url(app.config['VNPAY_PAYMENT_URL'], app.config['VNPAY_HASH_SECRET_KEY'])
        print(vnpay_payment_url)
        return redirect(vnpay_payment_url)


@payment_bp.route('/payment_return', methods=['GET'])
def payment_return():
    inputData = request.args
    if inputData:
        vnp = vnpay()
        vnp.responseData = dict(inputData)
        order_id = inputData.get('vnp_TxnRef')
        amount = int(inputData.get('vnp_Amount')) / 100
        order_desc = inputData.get('vnp_OrderInfo')
        vnp_TransactionNo = inputData.get('vnp_TransactionNo')
        vnp_ResponseCode = inputData.get('vnp_ResponseCode')
        # vnp_TmnCode = inputData['vnp_TmnCode']
        # vnp_PayDate = inputData['vnp_PayDate']
        # vnp_BankCode = inputData['vnp_BankCode']
        # vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(app.config['VNPAY_HASH_SECRET_KEY']):
            if vnp_ResponseCode == "00":
                return render_template("payment/payment_return.html", title="Kết quả thanh toán", 
                                       result="Thành công", 
                                       order_id=order_id, 
                                       amount=amount, 
                                       order_desc=order_desc, 
                                       vnp_TransactionNo=vnp_TransactionNo,
                                       vnp_ResponseCode=vnp_ResponseCode)
            else:
                return render_template("payment/payment_return.html", title="Kết quả thanh toán", 
                                       result="Lỗi", 
                                       order_id=order_id,
                                       amount=amount, 
                                       order_desc=order_desc, 
                                       vnp_TransactionNo=vnp_TransactionNo,
                                       vnp_ResponseCode=vnp_ResponseCode)
        else:
            return render_template("payment/payment_return.html", title="Kết quả thanh toán", 
                                    result="Lỗi",
                                    order_id=order_id, 
                                    amount=amount, 
                                    order_desc=order_desc, 
                                    vnp_TransactionNo=vnp_TransactionNo,
                                    vnp_ResponseCode=vnp_ResponseCode, msg="Sai checksum")
    return render_template("payment/payment_return.html", title="Kết quả thanh toán", result="")