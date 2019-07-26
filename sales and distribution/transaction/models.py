from django.db import models
from inventory.models import Add_item
from django.contrib.auth.models import User
import datetime


class ChartOfAccount(models.Model):
    account_title = models.CharField(max_length = 100, unique = True)
    parent_id = models.IntegerField()
    opening_balance = models.DecimalField(max_digits = 8, decimal_places = 2)
    phone_no = models.CharField(max_length = 100)
    email_address = models.CharField(max_length = 100)
    ntn = models.CharField(max_length = 100)
    stn = models.CharField(max_length = 100)
    cnic = models.CharField(max_length = 100)
    Address = models.CharField(max_length = 200)
    remarks = models.CharField(max_length = 100)
    credit_limit = models.DecimalField(max_digits = 8, decimal_places = 2)


class PurchaseHeader(models.Model):
    purchase_no = models.CharField(max_length = 100, unique = True)
    date = models.DateField(default=datetime.date.today)
    footer_description = models.TextField()
    follow_up = models.DateField(default = datetime.date.today)
    payment_method = models.CharField(max_length = 100)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL, blank=True, null=True,)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)


class PurchaseReturnHeader(models.Model):
    purchase_return_no = models.CharField(max_length = 100, unique = True)
    date = models.DateField(default=datetime.date.today)
    footer_description = models.TextField()
    follow_up = models.DateField(default = datetime.date.today)
    payment_method = models.CharField(max_length = 100)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL, blank=True, null=True,)



class PurchaseReturnDetail(models.Model):
    item_id = models.ForeignKey(Add_item, models.SET_NULL, blank=True, null=True)
    item_description = models.TextField()
    width = models.DecimalField(max_digits = 8, decimal_places = 2)
    height = models.DecimalField(max_digits = 8, decimal_places = 2)
    quantity = models.DecimalField(max_digits = 8, decimal_places = 2)
    meas = models.CharField(max_length = 100)
    rate = models.DecimalField(max_digits = 8, decimal_places = 2)
    purchase_return_id = models.ForeignKey(PurchaseReturnHeader, on_delete = models.CASCADE)

class PurchaseDetail(models.Model):
    item_id = models.ForeignKey(Add_item, models.SET_NULL, blank=True, null=True)
    item_description = models.TextField()
    width = models.DecimalField(max_digits = 8, decimal_places = 2)
    height = models.DecimalField(max_digits = 8, decimal_places = 2)
    quantity = models.DecimalField(max_digits = 8, decimal_places = 2)
    meas = models.CharField(max_length = 100)
    rate = models.DecimalField(max_digits = 8, decimal_places = 2)
    total_amount = models.DecimalField(max_digits = 8, decimal_places = 2)
    purchase_id = models.ForeignKey(PurchaseHeader, on_delete = models.CASCADE)



class SaleHeader(models.Model):
    sale_no = models.CharField(max_length = 100, unique = True)
    date = models.DateField(default = datetime.date.today)
    footer_description = models.TextField()
    credit_days = models.IntegerField()
    follow_up = models.DateField(default = datetime.date.today)
    payment_method = models.CharField(max_length = 100)
    account_holder = models.CharField(max_length = 100)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL,blank=True,null=True)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)


class SaleDetail(models.Model):
    item_id = models.ForeignKey(Add_item, models.SET_NULL, blank=True, null=True)
    item_description = models.TextField()
    width = models.DecimalField(max_digits = 8, decimal_places = 2)
    height = models.DecimalField(max_digits = 8, decimal_places = 2)
    quantity = models.DecimalField(max_digits = 8, decimal_places = 2)
    meas = models.CharField(max_length = 100)
    rate = models.DecimalField(max_digits = 8, decimal_places = 2)
    sale_id = models.ForeignKey(SaleHeader, on_delete = models.CASCADE)
    total_amount = models.DecimalField(max_digits = 8, decimal_places = 2)


class SaleReturnHeader(models.Model):
    sale_return_no = models.CharField(max_length = 100, unique = True)
    date = models.DateField(default = datetime.date.today)
    footer_description = models.TextField()
    follow_up = models.DateField(default = datetime.date.today)
    payment_method = models.CharField(max_length = 100)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL,blank=True,null=True,)


class SaleReturnDetail(models.Model):
    item_id = models.ForeignKey(Add_item, models.SET_NULL, blank=True, null=True)
    item_description = models.TextField()
    width = models.DecimalField(max_digits = 8, decimal_places = 2)
    height = models.DecimalField(max_digits = 8, decimal_places = 2)
    quantity = models.DecimalField(max_digits = 8, decimal_places = 2)
    meas = models.CharField(max_length = 100)
    rate = models.DecimalField(max_digits = 8, decimal_places = 2)
    sale_return_id = models.ForeignKey(SaleReturnHeader, on_delete = models.CASCADE)


class Company_info(models.Model):
    company_name = models.CharField(max_length = 100)
    company_address = models.TextField()
    company_logo = models.TextField()
    phone_no = models.CharField(max_length = 100)
    mobile_no = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    website = models.CharField(max_length = 100)


class VoucherHeader(models.Model):
    voucher_no = models.CharField(max_length = 100)
    doc_no = models.CharField(max_length = 100)
    doc_date = models.DateField(default = datetime.date.today)
    cheque_no = models.CharField(max_length = 100)
    cheque_date = models.DateField(max_length = datetime.date.today)
    description = models.TextField()
    invoice_id = models.ForeignKey(SaleHeader, models.SET_NULL, blank=True,null=True)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)


class VoucherDetail(models.Model):
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL,blank=True,null=True)
    debit = models.DecimalField(max_digits = 8, decimal_places = 2)
    credit = models.DecimalField(max_digits = 8, decimal_places = 2)
    invoice_id = models.IntegerField()
    header_id = models.ForeignKey(VoucherHeader, models.SET_NULL,blank=True,null=True)

class Transactions(models.Model):
    refrence_id = models.CharField(max_length = 100)
    refrence_date = models.DateField(blank = True)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL,blank=True,null=True)
    tran_type = models.CharField(max_length = 100)
    amount = models.DecimalField(max_digits = 8, decimal_places = 2)
    date = models.DateField(default = datetime.date.today)
    ref_inv_tran_id = models.IntegerField()
    ref_inv_tran_type = models.CharField(max_length = 100)
    voucher_id = models.ForeignKey(VoucherHeader, models.SET_NULL, blank = True, null = True)
    remarks = models.CharField(max_length = 100)


class JobOrderHeader(models.Model):
    job_no = models.CharField(max_length = 100)
    file_name = models.CharField(max_length = 100)
    date = models.DateField(default = datetime.date.today)
    delivery_date = models.DateField(default = datetime.date.today)
    remarks = models.CharField(max_length = 100)
    account_id = models.ForeignKey(ChartOfAccount, models.SET_NULL,blank=True,null=True)


class JobOrderDetail(models.Model):
    item_id = models.ForeignKey(Add_item, models.SET_NULL, blank=True, null=True)
    width = models.DecimalField(max_digits = 8, decimal_places = 2)
    height = models.DecimalField(max_digits = 8, decimal_places = 2)
    quantity = models.DecimalField(max_digits = 8, decimal_places = 2)
    remarks = models.CharField(max_length = 100)
    meas = models.CharField(max_length = 100)
    header_id = models.ForeignKey(JobOrderHeader, models.SET_NULL, blank = True, null = True)
