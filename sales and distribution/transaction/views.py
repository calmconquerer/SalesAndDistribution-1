from django.shortcuts import render, redirect
from inventory.models import Add_item
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import (ChartOfAccount, PurchaseHeader, PurchaseReturnHeader, PurchaseDetail, SaleHeader, SaleDetail,
                    Company_info, SaleReturnDetail, SaleReturnHeader, VoucherHeader, VoucherDetail, Transactions,
                    JobOrderHeader, JobOrderDetail)
import datetime, json
from .utils import render_to_pdf
from django.template.loader import get_template
from django.db import connection
from django.contrib import messages
from django.db.models import Q


@login_required()
def home(request):
    return render(request, 'transaction/index.html')


@login_required()
def purchase(request):
    all_purchases = PurchaseHeader.objects.all()
    return render(request, 'transaction/purchase.html', {'all_purchases': all_purchases})


@login_required()
def new_purchase(request):
    total_amount = 0
    serial = "1"
    last_purchase_no = PurchaseHeader.objects.last()
    all_item_code = Add_item.objects.all()
    all_accounts = ChartOfAccount.objects.all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_purchase_no:
        last_purchase_no = last_purchase_no.purchase_no[6:]
        serial = str((int(last_purchase_no) + 1))
        last_purchase_no = date[2:]+'PI'+serial
    else:
        last_purchase_no =  date[2:]+'PI1'
    item_code = request.POST.get('item_code_purchase')
    if item_code:
        items = Add_item.objects.filter(item_code = item_code)
        print(items)
        items = serializers.serialize('json',items)
        return JsonResponse({"items":items})
    if request.method == "POST":
        purchase_id = request.POST.get('purchase_id',False)
        vendor = request.POST.get('vendor',False)
        follow_up = request.POST.get('follow_up',False)
        payment_method = request.POST.get('payment_method',False)
        footer_desc = request.POST.get('footer_desc',False)
        account_id = ChartOfAccount.objects.get(account_title = vendor)
        date = datetime.date.today()

        if follow_up:
            follow_up = follow_up
        else:
            follow_up = '2010-06-10'

        purchase_header = PurchaseHeader(purchase_no = purchase_id, date = date, footer_description = footer_desc, payment_method = payment_method, account_id = account_id, follow_up = follow_up)
        items = json.loads(request.POST.get('items'))
        purchase_header.save()
        header_id = PurchaseHeader.objects.get(purchase_no = purchase_id)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], purchase_id = header_id)
            purchase_detail.save()
            total_amount = total_amount + float(value["total"])
        print(total_amount)
        header_id = header_id.id

        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id)
            tran2.save()
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id)
            tran1.save()
        else:
            purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice On Credit", amount = -abs(total_amount), date = date, remarks = purchase_id)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = purchase_account, tran_type = "Purchase Invoice On Credit", amount = total_amount, date = date, remarks = purchase_id)
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_purchase.html',{"all_accounts":all_accounts,"last_purchase_no":last_purchase_no, 'all_item_code':all_item_code})


@login_required()
def edit_purchase(request, pk):
    all_item_code = Add_item.objects.all()
    purchase_header = PurchaseHeader.objects.filter(id=pk).first()
    purchase_detail = PurchaseDetail.objects.filter(purchase_id=pk).all()
    all_accounts = ChartOfAccount.objects.all()
    item_code_purchase = request.POST.get('item_code_purchase', False)
    print(item_code_purchase)
    if item_code_purchase:
        data = Add_item.objects.filter(item_code = item_code_purchase)
        items = serializers.serialize('json', data)
        print(items)
        return HttpResponse(json.dumps({'items': items}))
    if request.method == 'POST':
        purchase_detail.delete()
        purchase_id = request.POST.get('purchase_id', False)
        supplier = request.POST.get('supplier', False)
        follow_up = request.POST.get('follow_up', False)
        payment_method = request.POST.get('payment_method', False)
        footer_desc = request.POST.get('footer_desc', False)
        account_id = ChartOfAccount.objects.get(account_title=supplier)
        print(follow_up)
        if follow_up:
            follow_up = follow_up
        else:
            follow_up = '2010-06-10'
        date = datetime.date.today()
        purchase_header.follow_up = follow_up
        purchase_header.payment_method = payment_method
        purchase_header.footer_description = footer_desc
        purchase_header.account_id = account_id

        purchase_header.save()

        items = json.loads(request.POST.get('items'))
        purchase_header.save()
        header_id = PurchaseHeader.objects.get(purchase_no=purchase_id)
        for value in items:
            item_id = Add_item.objects.get(id = value["id"])
            purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"],meas = value["measurment"], rate = value["rate"] ,purchase_id=header_id)
            purchase_detail.save()
        return JsonResponse({'result': 'success'})
    return render(request, 'transaction/edit_purchase.html',
                  {'all_item_code': all_item_code, 'all_accounts': all_accounts, 'purchase_header': purchase_header,
                   'purchase_detail': purchase_detail, 'pk': pk})


@login_required()
def purchase_return_summary(request):
    all_purchase_return = PurchaseReturnHeader.objects.all()
    return render(request, 'transaction/purchase_return_summary.html', {'all_purchase_return': all_purchase_return})


def new_purchase_return(request):
    return render(request, 'transaction/purchase_return.html')


@login_required()
def sale(request):
    all_sales = SaleHeader.objects.all()
    return render(request, 'transaction/sale.html',{"all_sales": all_sales})


@login_required()
def new_sale(request):
    total_amount = 0
    serial = "0"
    last_sale_no = SaleHeader.objects.last()
    all_job_order = JobOrderHeader.objects.all()
    all_accounts = ChartOfAccount.objects.filter(parent_id = 7).all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_sale_no:
        last_sale_no = last_sale_no.sale_no[6:]
        serial = str((int(last_sale_no)+1))
        last_sale_no = date[2:]+'SI'+serial
    else:
        last_sale_no =  date[2:]+'SI1'
    job_no_sale = request.POST.get('job_no_sale')
    if job_no_sale:
        header_job = JobOrderHeader.objects.get(job_no = job_no_sale)
        cursor = connection.cursor()
        items = cursor.execute('''select inventory_add_item.item_code, inventory_add_item.item_name, inventory_add_item.item_description,transaction_joborderdetail.meas, transaction_joborderdetail.width, transaction_joborderdetail.height, transaction_joborderdetail.quantity
                                from transaction_joborderdetail
                                inner join inventory_add_item on transaction_joborderdetail.item_id_id = inventory_add_item.id
                                where transaction_joborderdetail.header_id_id = %s
                                ''',[header_job.id])
        items = items.fetchall()
        return JsonResponse({"items":items})
    if request.method == "POST":
        sale_id = request.POST.get('sale_id',False)
        customer = request.POST.get('customer',False)
        account_holder = request.POST.get('account_holder',False)
        credit_days = request.POST.get('credit_days',False)
        payment_method = request.POST.get('payment_method',False)
        footer_desc = request.POST.get('footer_desc',False)
        account_id = ChartOfAccount.objects.get(account_title = customer)
        date = datetime.date.today()
        start_date = str(date)
        get_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        follow_up = get_date + datetime.timedelta(days=int(credit_days))
        follow_up = datetime.datetime.strftime(follow_up, "%Y-%m-%d")

        sale_header = SaleHeader(sale_no = last_sale_no, date = date, footer_description = footer_desc, payment_method = payment_method, account_id = account_id, account_holder = account_holder, credit_days = credit_days ,follow_up = follow_up)
        sale_header.save()
        items = json.loads(request.POST.get('items'))
        header_id = SaleHeader.objects.get(sale_no = sale_id)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            total_amount = total_amount + float(value["total"])
            sale_detail = SaleDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], sale_id = header_id, total_amount = total_amount)
            sale_detail.save()

        header_id = header_id.id
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        else:
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice On Credit", amount = total_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = sale_account, tran_type = "Sale Invoice On Credit", amount = -abs(total_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_sale.html',{"all_accounts":all_accounts,"last_sale_no":last_sale_no, 'all_job_order':all_job_order})

@login_required()
def delete_sale(request,pk):
    refrence_id = Q(refrence_id = pk)
    tran_type = Q(tran_type = "Sale Invoice")
    ref_inv_tran_id = Q(ref_inv_tran_id = pk)
    ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    Transactions.objects.filter(refrence_id , tran_type | ref_inv_tran_id | ref_inv_tran_type).all().delete()
    SaleDetail.objects.filter(sale_id = pk).all().delete()
    SaleHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Sale Invoice Deleted")
    return redirect('sale')

@login_required()
def edit_sale(request, pk):
    total_amount = 0
    job_no = JobOrderHeader.objects.all()
    sale_header = SaleHeader.objects.filter(id=pk).first()
    sale_detail = SaleDetail.objects.filter(sale_id=pk).all()
    all_accounts = ChartOfAccount.objects.all()
    item_code = request.POST.get('job_no_sale', False)

    if item_code:
        header_job = JobOrderHeader.objects.get(job_no = item_code)
        cursor = connection.cursor()
        items = cursor.execute('''select inventory_add_item.item_code, inventory_add_item.item_name, inventory_add_item.item_description,transaction_joborderdetail.meas, transaction_joborderdetail.width, transaction_joborderdetail.height, transaction_joborderdetail.quantity
                                from transaction_joborderdetail
                                inner join inventory_add_item on transaction_joborderdetail.item_id_id = inventory_add_item.id
                                where transaction_joborderdetail.header_id_id = %s
                                ''',[header_job.id])
        items = items.fetchall()
        return JsonResponse({"items":items})
    if request.method == 'POST':
        sale_detail.delete()

        sale_id = request.POST.get('sale_id', False)
        customer = request.POST.get('customer', False)
        account_holder = request.POST.get('account_holder', False)
        credit_days = request.POST.get('credit_days', False)
        print(credit_days)
        payment_method = request.POST.get('payment_method', False)
        footer_desc = request.POST.get('footer_desc', False)
        print(customer)
        account_id = ChartOfAccount.objects.get(account_title=customer)
        print(account_id)
        date = datetime.date.today()
        start_date = str(date)
        get_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        follow_up = get_date + datetime.timedelta(days=int(credit_days))
        follow_up = datetime.datetime.strftime(follow_up, "%Y-%m-%d")


        sale_header.follow_up = follow_up
        sale_header.credit_days = credit_days
        sale_header.account_holder = account_holder
        sale_header.payment_method = payment_method
        sale_header.footer_description = footer_desc
        sale_header.account_id = account_id

        sale_header.save()

        items = json.loads(request.POST.get('items'))
        sale_header.save()
        header_id = SaleHeader.objects.get(sale_no=sale_id)
        for value in items:
            total_amount = total_amount + float(value["total"])
            item_id = Add_item.objects.get(item_code = value["id"])
            sale_detail = SaleDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], sale_id = header_id, total_amount = total_amount)
            sale_detail.save()
        header_id = header_id.id
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type | ref_inv_tran_id | ref_inv_tran_type).all().delete()
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        else:
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type | ref_inv_tran_id | ref_inv_tran_type).all().delete()
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = sale_account, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/edit_sale.html',
                  {'job_no': job_no, 'sale_header': sale_header, 'sale_detail': sale_detail,'pk':pk})


@login_required()
def sale_return_summary(request):
    all_sales_return = SaleReturnHeader.objects.all()
    return render(request, 'transaction/sale_return_summary.html', {'all_sales_return': all_sales_return})


def new_sale_return(request):
    return render(request, 'transaction/sale_return.html')


@login_required()
def chart_of_account(request):
    all_accounts_null = ChartOfAccount.objects.filter(parent_id = 0).all()
    all_accounts = ChartOfAccount.objects.all()

    if request.method == 'POST':
        account_title = request.POST.get('account_title')
        account_type = request.POST.get('account_type')
        opening_balance = request.POST.get('opening_balance')
        phone_no = request.POST.get('phone_no')
        email_address = request.POST.get('email_address')
        ntn = request.POST.get('ntn')
        stn = request.POST.get('stn')
        cnic = request.POST.get('cnic')
        address = request.POST.get('address')
        remarks = request.POST.get('remarks')
        op_type = request.POST.get('optradio')
        credit_limits = request.POST.get('credit_limits')

        if opening_balance is "":
            opening_balance = 0.00
        if op_type == "credit":
            opening_balance = -abs(int(opening_balance))
        if credit_limits is "":
            credit_limits = 0.00
        coa = ChartOfAccount(account_title = account_title, parent_id = account_type, opening_balance = opening_balance, phone_no = phone_no, email_address = email_address, ntn = ntn, stn = stn, cnic = cnic ,Address = address, remarks = remarks, credit_limit=credit_limits)
        coa.save()
    return render(request, 'transaction/chart_of_account.html',{'all_accounts_null':all_accounts_null,'all_accounts':all_accounts})



@login_required()
def print_purchase(request,pk):
    lines = 0
    total_amount = 0
    total_quantity = 0
    total_square_fit = 0
    square_fit = 0
    header = PurchaseHeader.objects.filter(id = pk).first()
    detail = PurchaseDetail.objects.filter(purchase_id = pk).all()
    image = Company_info.objects.first()
    for value in detail:
        lines = lines + len(value.item_description.split('\n'))
        square_fit = float(value.width * value.height)
        gross = square_fit * float(value.rate)
        amount = gross * float(value.quantity)
        total_amount = total_amount + amount
        total_quantity = (total_quantity + value.quantity)
        square_fit = value.height * value.width
        total_square_fit = total_square_fit + square_fit
    lines = lines + len(detail) + len(detail)
    total_lines = 36 - lines
    pdf = render_to_pdf('transaction/purchase_pdf.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Purchase_%s.pdf" %(header.purchase_no)
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def print_sale(request, pk):
    lines = 0
    total_amount = 0
    total_quantity = 0
    total_square_fit = 0
    square_fit = 0
    header = SaleHeader.objects.filter(id = pk).first()
    detail = SaleDetail.objects.filter(sale_id = pk).all()
    image = Company_info.objects.first()
    for value in detail:
        if value.meas == "sq.ft":
            square_fit = float(value.width * value.height)
            gross = square_fit * float(value.rate)
            amount = gross * float(value.quantity)
            total_amount = total_amount + amount
            total_quantity = (total_quantity + value.quantity)
            square_fit = value.height * value.width * value.quantity
            total_square_fit = total_square_fit + square_fit
        else:
            square_fit = float(value.width * value.height) / 144
            gross = square_fit * float(value.rate)
            amount = gross * float(value.quantity)
            total_amount = total_amount + amount
            total_quantity = (total_quantity + value.quantity)
            square_fit = value.height * value.width * value.quantity / 144
            total_square_fit = total_square_fit + square_fit

    pdf = render_to_pdf('transaction/sale_pdf.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Sale_%s.pdf" % (header.sale_no)
        content = "inline; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def journal_voucher(request):
    serial = "1"
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%JV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[6:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'JV'+serial
    else:
        get_last_tran_id =  date[2:]+'JV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no="-",
                                  cheque_date=doc_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id=header_id)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])),header_id=header_id)
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/journal_voucher.html',{"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id})


@login_required()
def delete_journal_voucher(request, pk):
    ref = VoucherHeader.objects.get(id = pk)
    refrence_id = Q(refrence_id = ref.doc_no)
    tran_type = Q(tran_type = "JV")
    Transactions.objects.filter(refrence_id, tran_type).all().delete()
    VoucherDetail.objects.filter(header_id = ref.id).all().delete()
    VoucherHeader.objects.filter(doc_no = ref.doc_no).delete()
    messages.add_message(request, messages.SUCCESS, "Journal Voucher Deleted")
    return redirect('journal-voucher-summary')

def bank_receiving_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%BRV%' ''')
    print(all_vouchers)
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/bank_receiving_voucher.html', {'all_vouchers': all_vouchers})


def new_bank_receiving_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%BRV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()
    print(get_last_tran_id)

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        # count = last_sale_no.count('0')
        get_last_tran_id = date[2:]+'BRV'+serial
    else:
        get_last_tran_id =  date[2:]+'BRV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no=cheque_no,
                                  cheque_date=cheque_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='BRV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00, header_id = header_id)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='BRV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])), header_id = header_id)
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/new_bank_receiving_voucher.html', {'all_accounts': all_accounts, 'get_last_tran_id': get_last_tran_id})


def new_bank_payment_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%BPV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()
    print(get_last_tran_id)

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        # count = last_sale_no.count('0')
        get_last_tran_id = date[2:]+'BPV'+serial
    else:
        get_last_tran_id =  date[2:]+'BPV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)
        description = request.POST.get('description', False)
        items = json.loads(request.POST.get('items', False))
        if cheque_date:
            cheque_date = cheque_date
        else:
            cheque_date = "2010-10-06"
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no=cheque_no,
                                  cheque_date=cheque_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            print("this")
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='CRV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id = header_id)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='CRV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])))
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/new_bank_payment_voucher.html', {'all_accounts': all_accounts, 'get_last_tran_id': get_last_tran_id})


def bank_payment_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%BPV%' ''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/bank_payment_voucher.html', {'all_vouchers': all_vouchers})


def reports(request):
    all_accounts = ChartOfAccount.objects.all()
    return render(request, 'transaction/reports.html', {'all_accounts': all_accounts})


def trial_balance(request):
    if request.method == 'POST':
        debit_amount = 0
        credit_amount = 0
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        company_info = Company_info.objects.all()
        cursor = connection.cursor()
        cursor.execute('''Select id,account_title,ifnull(amount,0) + opening_balance As Amount
                        from transaction_chartofaccount
                        Left Join
                        (select account_id_id,sum(AMount) As Amount from transaction_transactions
                        Where transaction_transactions.date Between %s And %s
                        Group By account_id_id) As tbltran On transaction_chartofaccount.id = tbltran.account_id_id
                        ''',[from_date, to_date])
        row = cursor.fetchall()
        for value in row:
            if value[2] >= 0:
                debit_amount = debit_amount + value[2]
            else:
                credit_amount = credit_amount + value[2]
        pdf = render_to_pdf('transaction/trial_balance_pdf.html', {'company_info':company_info, 'row': row, 'debit_amount': debit_amount, 'credit_amount': credit_amount,'from_date':from_date,'to_date':to_date})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'TrialBalance%s.pdf' %('000')
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not Found")
    return redirect('report')


def account_ledger(request):
    if request.method == "POST":
        debit_amount = 0
        credit_amount = 0
        pk = request.POST.get('account_title')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        company_info = Company_info.objects.all()
        image = Company_info.objects.filter(id=1).first()
        cursor = connection.cursor()
        cursor.execute('''Select tran_type,refrence_id,refrence_date,date,remarks,
                        Case When amount > -1 Then  amount Else 0 End As Debit,
                        Case When amount < -1 Then  amount Else 0 End As Credit
                        From transaction_transactions
                        Where transaction_transactions.date Between %s And %s and transaction_transactions.account_id_id = %s
                        Order By refrence_date Asc
                    ''',[from_date, to_date, pk])
        row = cursor.fetchall()
        print(row)
        for value in row:
            print(value)
        if row:
            for v in row:
                if v[5] >= 0:
                    debit_amount = debit_amount + v[5]
                if v[6] <= 0:
                    credit_amount = credit_amount + v[6]
        account_id = ChartOfAccount.objects.filter(id = pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/account_ledger_pdf.html', {'company_info':company_info,'image':image,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "TrialBalance%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


def cash_receiving_voucher(request):
    cursor = connection.cursor()
    all_vouchers = VoucherHeader.objects.all()
    return render(request, 'transaction/cash_receiving_voucher.html', {'all_vouchers': all_vouchers})


def new_cash_receiving_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CRV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CRV'+serial
    else:
        get_last_tran_id =  date[2:]+'CRV1'
    account_name = request.POST.get('account_title', False)
    check = request.POST.get('check', False)
    invoice_no = request.POST.get('invoice_no', False)
    print(invoice_no)
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = SaleHeader.objects.all()
    user = request.user
    if account_name:
        if check == "1":
            print(invoice_no)
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.sale_no = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s AND HD.sale_no = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
        else:
            print("Humayun")
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,id.id,id.id])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
    if request.method == "POST":
        invoice_no = request.POST.get('invoice_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        customer = request.POST.get('customer', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no = get_last_tran_id, doc_no = invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            invoice_no = SaleHeader.objects.get(sale_no = value["invoice_no"])

            account_id = ChartOfAccount.objects.get(account_title = customer)
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["debit"]) - float(value['balance'])

            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = description, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = description, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = amount, credit = 0.00, header_id = header_id, invoice_id = invoice_no)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = 0.00, credit = -abs(amount),header_id = header_id, invoice_id = invoice_no)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_cash_receiving_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})

def view_cash_receiving(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_receiving_voucher.html', {'voucher_header': voucher_header,'voucher_detail': voucher_detail})

def delete_cash_receiving(request,pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Receiving Voucher Deleted")
    return redirect('cash-receiving-voucher')

def cash_payment_voucher(request):
    cursor = connection.cursor()
    all_vouchers = VoucherHeader.objects.all()
    return render(request, 'transaction/cash_payment_voucher.html', {'all_vouchers': all_vouchers})


def new_cash_receiving_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CRV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CRV'+serial
    else:
        get_last_tran_id =  date[2:]+'CRV1'
    account_name = request.POST.get('account_title', False)
    check = request.POST.get('check', False)
    invoice_no = request.POST.get('invoice_no', False)
    print(invoice_no)
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = SaleHeader.objects.all()
    user = request.user
    if account_name:
        if check == "1":
            print(invoice_no)
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.sale_no = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s AND HD.sale_no = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
        else:
            print("Humayun")
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,id.id,id.id])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
    if request.method == "POST":
        invoice_no = request.POST.get('invoice_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        customer = request.POST.get('customer', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no = get_last_tran_id, doc_no = invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            invoice_no = SaleHeader.objects.get(sale_no = value["invoice_no"])

            account_id = ChartOfAccount.objects.get(account_title = customer)
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["debit"]) - float(value['balance'])

            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = description, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = description, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = amount, credit = 0.00, header_id = header_id, invoice_id = invoice_no)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = 0.00, credit = -abs(amount),header_id = header_id, invoice_id = invoice_no)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_cash_receiving_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})

def view_cash_receiving(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_receiving_voucher.html', {'voucher_header': voucher_header,'voucher_detail': voucher_detail})

def delete_cash_receiving(request,pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Receiving Voucher Deleted")
    return redirect('cash-receiving-voucher')


def job_order(request):
    all_job_order = JobOrderHeader.objects.all()
    return render(request, 'transaction/job_order.html',{'all_job_order':all_job_order})


def new_job_order(request):
    serial = "1"
    last_job_no = JobOrderHeader.objects.last()
    all_item_code = Add_item.objects.all()
    all_accounts = ChartOfAccount.objects.all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_job_no:
        get_job_no = last_job_no.job_no[6:]
        serial = str((int(get_job_no) + 1))
        get_job_no = date[2:]+'JO'+serial
    else:
        get_job_no =  date[2:]+'JO'+serial
    item_code = request.POST.get('item_code', False)
    if item_code:
        row = Add_item.objects.filter(item_code = item_code)
        row = serializers.serialize('json',row)
        return HttpResponse(json.dumps({'row':row}))
    if request.method == 'POST':
        client_name = request.POST.get('client_name', False)
        file_name = request.POST.get('file_name', False)
        delivery_date = request.POST.get('delivery_date', False)
        remarks = request.POST.get('remarks', False)
        items = json.loads(request.POST.get('items'))
        if delivery_date:
            delivery_date = delivery_date
        else:
            delivery_date = "2010-10-06"
        account_id = ChartOfAccount.objects.get(account_title = client_name)
        job_order_header = JobOrderHeader(job_no = get_job_no, file_name = file_name, delivery_date = delivery_date, remarks = remarks, account_id = account_id)
        job_order_header.save()
        header_id = JobOrderHeader.objects.get(job_no = get_job_no)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            job_order_detail = JobOrderDetail(item_id = item_id, width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], header_id = header_id)
            job_order_detail.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_job_order.html',{"get_job_no":get_job_no,"all_item_code":all_item_code,"all_accounts":all_accounts})


def edit_job_order(request,pk):
    all_item_code = Add_item.objects.all()
    all_accounts = ChartOfAccount.objects.all()
    job_header = JobOrderHeader.objects.get(id = pk)
    job_detail = JobOrderDetail.objects.filter(header_id = pk).all()
    item_code = request.POST.get('item_code', False)
    if item_code:
        row = Add_item.objects.filter(item_code = item_code)
        row = serializers.serialize('json',row)
        return HttpResponse(json.dumps({'row':row}))
    if request.method == 'POST':
        job_detail.delete()
        client_name = request.POST.get('client_name', False)
        file_name = request.POST.get('file_name', False)
        delivery_date = request.POST.get('delivery_date', False)
        remarks = request.POST.get('remarks', False)
        items = json.loads(request.POST.get('items'))
        if delivery_date:
            delivery_date = delivery_date
        else:
            delivery_date = "2010-10-06"
        account_id = ChartOfAccount.objects.get(account_title = client_name)
        job_header.account_id = account_id
        job_header.file_name = file_name
        job_header.delivery_date = delivery_date
        job_header.remarks = remarks
        job_header.save()

        header_id = JobOrderHeader.objects.get(id = pk)
        for value in items:
            print("Hamza")
            print(value["id"])
            item_id = Add_item.objects.get(id = value["id"])
            print(item_id)
            job_order_detail = JobOrderDetail(item_id = item_id, width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], header_id = header_id)
            job_order_detail.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/edit_job_order.html',{"pk":pk,"all_item_code":all_item_code,"all_accounts":all_accounts, 'job_header':job_header, 'job_detail':job_detail})

def delete_job_order(request,pk):
    delete_job_order_detail = JobOrderDetail.objects.filter(header_id = pk).all().delete()
    delete_job_order_header = JobOrderHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Job Order Deleted")
    return redirect('job-order')

def edit_bank_receiving_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.cheque_no = cheque_no
        voucher_header.cheque_date = cheque_date
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass

    return render(request, 'transaction/edit_bank_receiving_voucher.html', {'voucher_header': voucher_header,
                                                                            'voucher_detail': voucher_detail, 'pk': pk,
                                                                            'all_accounts': all_accounts})


def journal_voucher_summary(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%JV%' ''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/journal_voucher_summary.html', {'all_vouchers': all_vouchers})


def edit_bank_payment_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.cheque_no = cheque_no
        voucher_header.cheque_date = cheque_date
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass
    return render(request, 'transaction/edit_bank_payment_voucher.html', {'voucher_header': voucher_header,
                                                                          'voucher_detail': voucher_detail,
                                                                          'all_accounts': all_accounts, 'pk': pk,
                                                                          'account_id': account_id})

def edit_cash_payment(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass

    return render(request, 'transaction/edit_cash_payment_voucher.html', {'voucher_header': voucher_header,
                                                                            'voucher_detail': voucher_detail,
                                                                            'all_accounts': all_accounts, 'pk': pk,
                                                                            'account_id': account_id})



def edit_journal_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    if request.method == 'POST':
        voucher_detail.delete()

        ref = VoucherHeader.objects.get(id = pk)
        refrence_id = Q(refrence_id = ref.doc_no)
        tran_type = Q(tran_type = "JV")
        Transactions.objects.filter(refrence_id, tran_type).all().delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.save()

        items = json.loads(request.POST.get('items'))
        header_id = VoucherHeader.objects.get(id = voucher_header.id)

        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=voucher_header.voucher_no, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id=header_id)
                jv_detail1.save()

            if value["credit"] > "0" and value["credit"] > "0.00":
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=voucher_header.voucher_no, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])),header_id=header_id)
                jv_detail2.save()
        return JsonResponse({"result": "success"})

    return render(request, 'transaction/edit_journal_voucher.html', {'voucher_header': voucher_header,
                                                                          'voucher_detail': voucher_detail,
                                                                          'all_accounts': all_accounts, 'pk': pk,
                                                                          'account_id': account_id})
