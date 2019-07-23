from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Add_item
from django.db import connection
import json
from django.contrib import messages


def add_item(request):
    get_item_code = Add_item.objects.last()
    if get_item_code:
        get_item_code = get_item_code.item_code
        serial_no = get_item_code[10:]
        serial_no = int(serial_no) + 1
    else:
        inc = 1
        serial_no = int('101')
    item_name = request.POST.get("item_name")
    item_desc = request.POST.get("item_desc")
    unit = request.POST.get("unit")
    type = request.POST.get("type")
    size = request.POST.get("size")
    opening_stock = request.POST.get("opening_stock")
    if item_name and item_desc and type and size:
        return JsonResponse({"item_name":item_name,"item_desc":item_desc,"unit":unit,"type":type,"size":size,"opening_stock":opening_stock})
    if request.method == "POST":
        items = json.loads(request.POST.get('items'))
        for value in items:
            type = value["type"][:5]
            size = value["size"]
            item_code = type+"-"+size+"-"+str(serial_no)
            new_products = Add_item(item_code = item_code, item_name = value["item_name"], item_description = value["item_desc"]  ,unit = value["unit"] ,opening_stock = value["opening_stock"], type = value["type"], size = value["size"])
            new_products.save()
            return JsonResponse({"success":"success"})
    return render(request,'inventory/add_item.html')


def stock(request):
    cursor = connection.cursor()
    stock = cursor.execute('''Select itemID,Size,item_code, item_name,Item_description,Unit,SUM(Quantity) As qty From (
                            Select 'Opening Stock' As TranType,ID As ItemID, Size, Item_Code, Item_name, Item_description, unit,Opening_Stock as Quantity
                            From inventory_add_item
                            union all
                            Select 'Purchase' As TranType,P.ID As ItemID,P.Size, P.Item_Code,P.Item_name,P.Item_description,P.unit,sum(H.width*H.height*H.Quantity)
                            From transaction_purchasedetail H Inner join inventory_add_item P On H.item_id_id = P.id
                            group by H.item_id_id
                            union All
                            Select 'Purchase Return' As TranType,P.ID As ItemID,P.Size,P.Item_Code,P.Item_name,P.Item_description,P.unit,sum(H.width*H.height*H.Quantity) * -1
                            From transaction_purchasereturndetail H Inner join inventory_add_item P On H.item_id_id = P.id
                            group by H.item_id_id
                            union all
                            Select 'Sale' As TranType,P.ID AS ItemID,P.Size,P.Item_Code,P.Item_name,P.Item_description,P.unit,sum(H.width*H.height*H.Quantity) * -1
                            From transaction_saledetail H Inner join inventory_add_item P On H.item_id_id = P.id
                            group by H.item_id_id
                            union all
                            Select 'Sale Return' As TranType,P.ID AS ItemID,P.Size,P.Item_Code,P.Item_name,P.Item_description,P.unit,sum(H.width*H.height*H.Quantity)
                            From transaction_salereturndetail H Inner join inventory_add_item P On H.item_id_id = P.id
                            group by H.item_id_id
                            ) As tblTemp
                            Group by ItemID''')
    stock = stock.fetchall()
    print(stock)
    return render(request,'inventory/stock.html',{'stock':stock})


def edit_item(request, pk):
    all_detail = Add_item.objects.filter(id = pk).first()
    if request.method == "POST":
        type = request.POST.get('type')
        size = request.POST.get('size')
        item_name = request.POST.get('item_name')
        item_name = item_name.upper()
        item_description = request.POST.get('item_desc')
        select_unit = request.POST.get('select_unit')
        opening_stock = request.POST.get('opening_stock')

        all_detail.type = type
        all_detail.size = size
        all_detail.item_name = item_name
        all_detail.item_description = item_description
        all_detail.select_unit = select_unit
        all_detail.opening_stock = opening_stock
        all_detail.save()
    return render(request, 'inventory/edit_item.html',{'all_detail':all_detail})


def item_avaliable(pk):
    cusror = connection.cursor()
    row = cusror.execute('''select case
                        when exists (select id from transaction_joborderdetail  where item_id_id = %s)
                        or exists (select id from transaction_purchasedetail  where item_id_id = %s)
                        or exists (select id from transaction_purchasereturndetail  where item_id_id = %s)
                        or exists (select id from transaction_saledetail  where item_id_id = %s)
                        or exists (select id from transaction_salereturndetail  where item_id_id = %s)
                        then 'y'
                        else 'n'
                        end''',[pk,pk,pk,pk,pk])
    row = row.fetchall()
    res_list = [x[0] for x in row]
    if res_list[0] == "n":
        Add_item.objects.filter(id = pk).delete()
        messages.add_message(request, messages.SUCCESS, "Item Deleted")
        return True
    else:
        return False


def delete_item(request, pk):
    item = item_avaliable(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Item Deleted.")
        return redirect('stock')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this item, it is refrenced.")
        return redirect('stock')
