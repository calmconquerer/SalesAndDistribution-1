$(document).ready(function(){


    function getCookie(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
     }


     // $('.add-item-purchase').click(function(){
     //   item_code_purchase = $('#item_code_purchase').val();
     //   $.ajax({
     //     headers: { "X-CSRFToken": getCookie("csrftoken") },
     //     type: 'POST',
     //     url: '/transaction/purchase/new/',
     //     data:{
     //       item_code_purchase:item_code_purchase,
     //     }
     //   })
     //   .done(function done(data){
     //    row =  JSON.parse(data.row);
     //       var index = $("table tbody tr:last-child").index();
     //           var row = '<tr>' +
     //               '<td>'+count+'</td>' +
     //               '<td>'+ row[0].fields["item_code"] +'</td>' +
     //               '<td><pre>'+ row[0].fields["item_description"] +'</pre></td>'+
     //               '<td><input type="text" class="form-control form-control-sm" value=""></td>' +
     //               '<td id="width" ><input type="text" class="form-control form-control-sm" value=""></td>' +
     //               '<td id="height"><input type="text" class="form-control form-control-sm" value=""></td>' +
     //               '<td>'+ row[0].fields["unit"] +'</td>' +
     //               '<td id="quantity"><input type="text" class="form-control form-control-sm" value=""></td>' +
     //               '<td id="square_fit" ></td>' +
     //               '<td id="rate"><input type="text" class="form-control form-control-sm" value=""></td>' +
     //               '<td id="amount"></td>' +
     //         '<td><a class="add-purchase" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-purchase" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-purchase" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
     //           '</tr>';
     //         $("table").append(row);
     //       $("table tbody tr").eq(index + 1).find(".add-purchase, .edit-purchase").toggle();
     //           $('[data-toggle="tooltip"]').tooltip();
     //   });
     // });
     //
     //         // Add row on add button click
     //     $(document).on("click", ".add-purchase", function(){
     //       sum = 0;
     //     var empty = false;
     //     var input = $(this).parents("tr").find('input[type="text"]');
     //         input.each(function(){
     //       if(!$(this).val()){
     //         $(this).addClass("error");
     //         empty = true;
     //       }
     //       else{
     //           $(this).removeClass("error");
     //           }
     //     });
     //     $(this).parents("tr").find(".error").first().focus();
     //     if(!empty){
     //       input.each(function(){
     //         $(this).parent("td").html($(this).val());
     //       });
     //       $(this).parents("tr").find(".add-purchase, .edit-purchase").toggle();
     //       $(".add-item-purchase").removeAttr("disabled");
     //     }
     //
     //     var get_width = $($(this).parents("tr").find("#width")).filter(function() {
     //             width = $(this).text();
     //             return width;
     //         }).closest("tr");
     //
     //     var get_height = $($(this).parents("tr").find("#height")).filter(function() {
     //             height = $(this).text();
     //             return height;
     //         }).closest("tr");
     //
     //     var square_fit = (width * height).toFixed(2);
     //
     //     var amount = $($(this).parents("tr").find("#square_fit")).filter(function() {
     //              $(this).text(square_fit);
     //         }).closest("tr");
     //
     //     var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
     //             rate = $(this).text();
     //             return rate;
     //         }).closest("tr");
     //
     //     var get_quantity = $($(this).parents("tr").find("#quantity")).filter(function() {
     //             quantity = $(this).text();
     //             return quantity;
     //         }).closest("tr");
     //
     //
     //     amount = square_fit * rate
     //     amount = amount * quantity
     //     var amount = $($(this).parents("tr").find("#amount")).filter(function() {
     //              $(this).text(amount.toFixed(2));
     //         }).closest("tr");
     //
     //
     //
     //     // var get_salesTax = $($(this).parents("tr").find("#sales_tax")).filter(function() {
     //     //         sales_tax = value_of_goods * $(this).text();
     //     //         sales_tax = sales_tax / 100
     //     //         return sales_tax;
     //     //     }).closest("tr");
     //     //
     //     // var set_salesTax = $($(this).parents("tr").find("#sales_tax_amount")).filter(function() {
     //     //         $(this).text(sales_tax.toFixed(2));
     //     //         return sales_tax;
     //     //     }).closest("tr");
     //     //
     //     // var set_total = $($(this).parents("tr").find("#total")).filter(function() {
     //     //         total = value_of_goods + sales_tax
     //     //         $(this).text(total.toFixed(2));
     //     //         return sales_tax;
     //     //     }).closest("tr");
     //     //
     //     //     $($(this).parents("tr").find("#total")).each(function() {
     //     //         var value = $(this).text();
     //     //         // add only if the value is number
     //     //         if(!isNaN(value) && value.length != 0) {
     //     //             console.log(value);
     //     //         }
     //     //   });
     //     //
     //     //   $('#new-purchase-table > tbody  > tr').each(function() {
     //     //      sum = sum + parseFloat($(this).find('td#total').text());
     //     //   });
     //     //
     //     // cartage_amount =	$('#cartage_amount').val();
     //     // additional_tax = $('#additional_tax').val();
     //     // console.log(sum);
     //     // grand = parseFloat(cartage_amount) + parseFloat(additional_tax) + sum;
     //     // $('#last_grand_total').val(grand.toFixed(2));
     //
     //     });
     //
     //     // Edit row on edit button click
     //      $(document).on("click", ".edit-purchase", function(){
     //        $(this).parents("tr").find("td:not(:last-child)").each(function(i){
     //        if (i === 3) {
     //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
     //        }
     //        if (i === 4) {
     //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
     //        }
     //        if (i === 5) {
     //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
     //        }
     //        if (i === 6) {
     //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
     //        }
     //        if (i === 8) {
     //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
     //        }
     //
     //        });
     //        $(this).parents("tr").find(".add-purchase, .edit-purchase").toggle();
     //        $(".add-item-purchase").attr("disabled", "disabled");
     //      });
     //
     //
     //      // Delete row on delete button click
     //        $(document).on("click", ".delete-purchase", function(){
     //          var row =  $(this).closest('tr');
     //          var siblings = row.siblings();
     //          siblings.each(function(index) {
     //          $(this).children('td').first().text(index + 1);
     //          });
     //          $(this).parents("tr").remove();
     //
     //        });
     //
     //
     //        $('#new-purchase-submit').on('submit',function(e){
     //        e.preventDefault();
     //        var table = $('#new-purchase-table');
     //        var data = [];
     //        var purchase_id = $('#purchase_id').val();
     //        var supplier = $('#supplier').val();
     //        var payment_method = $('#payment_method').val();
     //        var footer_desc = $('#footer_desc').val();
     //
     //        table.find('tr').each(function (i, el){
     //          if(i != 0)
     //          {
     //            var $tds = $(this).find('td');
     //            var row = {
     //              'item_code' : "",
     //              'item_name' : "",
     //              'description' : "",
     //              'width' : "",
     //              'height' : "",
     //              'unit' : "",
     //              'qty' : "",
     //              'rate' : "",
     //            };
     //            $tds.each(function(i, el){
     //              if (i === 1) {
     //                  row["item_code"] = ($(this).text());
     //              }
     //              if (i === 2) {
     //                  row["item_name"] = ($(this).text());
     //              }
     //              else if (i === 3) {
     //                  row["description"] = ($(this).text());
     //              }
     //              else if (i === 4) {
     //                  row["width"] = ($(this).text());
     //              }
     //              else if (i === 5) {
     //                  row["height"] = ($(this).text());
     //              }
     //              else if (i === 6) {
     //                  row["unit"] = ($(this).text());
     //              }
     //              else if (i === 7) {
     //                  row["qty"] = ($(this).text());
     //              }
     //              else if (i === 9) {
     //                  row["rate"] = ($(this).text());
     //              }
     //            });
     //            data.push(row);
     //          }
     //        });
     //
     //           req =	$.ajax({
     //              headers: { "X-CSRFToken": getCookie("csrftoken") },
     //              type: 'POST',
     //              url : '/transaction/purchase/new/',
     //              data:{
     //                'purchase_id': purchase_id,
     //                'supplier': supplier,
     //                'payment_method': payment_method,
     //                'footer_desc': footer_desc,
     //                'items': JSON.stringify(data),
     //              },
     //              dataType: 'json'
     //            })
     //            .done(function done(){
     //              alert("Purchase Created");
     //              location.reload();
     //            })
     //      });

// =============================================================================================================

        // $('.add-item-sale').click(function(){
        //   item_code_sale = $('#item_code_sale').val();
        //   $.ajax({
        //     headers: { "X-CSRFToken": getCookie("csrftoken") },
        //     type: 'POST',
        //     url: '/transaction/sale/new/',
        //     data:{
        //       item_code_purchase:item_code_sale,
        //     }
        //   })
        //   .done(function done(data){
        //    row =  JSON.parse(data.row);
        //       var index = $("table tbody tr:last-child").index();
        //           var row = '<tr>' +
        //               '<td>'+count+'</td>' +
        //               '<td>'+ row[0].fields["item_code"] +'</td>' +
        //               '<td><pre>'+ row[0].fields["item_description"] +'</pre></td>'+
        //               '<td><input type="text" class="form-control form-control-sm" value=""></td>' +
        //               '<td id="width" ><input type="text" class="form-control form-control-sm" value=""></td>' +
        //               '<td id="height"><input type="text" class="form-control form-control-sm" value=""></td>' +
        //               '<td>'+ row[0].fields["unit"] +'</td>' +
        //               '<td><input type="text" class="form-control form-control-sm" value=""></td>' +
        //               '<td id="square_fit" ></td>' +
        //               '<td id="rate"><input type="text" class="form-control form-control-sm" value=""></td>' +
        //               '<td id="amount"></td>' +
        //         '<td><a class="add-sale" title="Add" data-toggle="tooltip"><i class="material-icons">&#xE03B;</i></a><a class="edit-sale" title="Edit" data-toggle="tooltip"><i class="material-icons">&#xE254;</i></a><a class="delete-sale" title="Delete" data-toggle="tooltip"><i class="material-icons">&#xE872;</i></a></td>' +
        //           '</tr>';
        //         $("table").append(row);
        //       $("table tbody tr").eq(index + 1).find(".add-sale, .edit-sale").toggle();
        //           $('[data-toggle="tooltip"]').tooltip();
        //   });
        // });
        //
        //         // Add row on add button click
        //     $(document).on("click", ".add-sale", function(){
        //       sum = 0;
        //     var empty = false;
        //     var input = $(this).parents("tr").find('input[type="text"]');
        //         input.each(function(){
        //       if(!$(this).val()){
        //         $(this).addClass("error");
        //         empty = true;
        //       }
        //       else{
        //           $(this).removeClass("error");
        //           }
        //     });
        //     $(this).parents("tr").find(".error").first().focus();
        //     if(!empty){
        //       input.each(function(){
        //         $(this).parent("td").html($(this).val());
        //       });
        //       $(this).parents("tr").find(".add-sale, .edit-sale").toggle();
        //       $(".add-item-sale").removeAttr("disabled");
        //     }
        //
        //     var get_width = $($(this).parents("tr").find("#width")).filter(function() {
        //             width = $(this).text();
        //             return width;
        //         }).closest("tr");
        //
        //     var get_height = $($(this).parents("tr").find("#height")).filter(function() {
        //             height = $(this).text();
        //             return height;
        //         }).closest("tr");
        //
        //     var square_fit = (width * height).toFixed(2);
        //
        //     var amount = $($(this).parents("tr").find("#square_fit")).filter(function() {
        //              $(this).text(square_fit);
        //         }).closest("tr");
        //
        //     var get_rate = $($(this).parents("tr").find("#rate")).filter(function() {
        //             rate = $(this).text();
        //             return rate;
        //         }).closest("tr");
        //
        //     amount = square_fit * rate
        //
        //     var amount = $($(this).parents("tr").find("#amount")).filter(function() {
        //              $(this).text(amount.toFixed(2));
        //         }).closest("tr");
        //
        //
        //
        //     // var get_salesTax = $($(this).parents("tr").find("#sales_tax")).filter(function() {
        //     //         sales_tax = value_of_goods * $(this).text();
        //     //         sales_tax = sales_tax / 100
        //     //         return sales_tax;
        //     //     }).closest("tr");
        //     //
        //     // var set_salesTax = $($(this).parents("tr").find("#sales_tax_amount")).filter(function() {
        //     //         $(this).text(sales_tax.toFixed(2));
        //     //         return sales_tax;
        //     //     }).closest("tr");
        //     //
        //     // var set_total = $($(this).parents("tr").find("#total")).filter(function() {
        //     //         total = value_of_goods + sales_tax
        //     //         $(this).text(total.toFixed(2));
        //     //         return sales_tax;
        //     //     }).closest("tr");
        //     //
        //     //     $($(this).parents("tr").find("#total")).each(function() {
        //     //         var value = $(this).text();
        //     //         // add only if the value is number
        //     //         if(!isNaN(value) && value.length != 0) {
        //     //             console.log(value);
        //     //         }
        //     //   });
        //     //
        //     //   $('#new-purchase-table > tbody  > tr').each(function() {
        //     //      sum = sum + parseFloat($(this).find('td#total').text());
        //     //   });
        //     //
        //     // cartage_amount =	$('#cartage_amount').val();
        //     // additional_tax = $('#additional_tax').val();
        //     // console.log(sum);
        //     // grand = parseFloat(cartage_amount) + parseFloat(additional_tax) + sum;
        //     // $('#last_grand_total').val(grand.toFixed(2));
        //
        //     });
        //
        //     // Edit row on edit button click
        //      $(document).on("click", ".edit-sale", function(){
        //        $(this).parents("tr").find("td:not(:last-child)").each(function(i){
        //        if (i === 3) {
        //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        //        }
        //        if (i === 4) {
        //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        //        }
        //        if (i === 5) {
        //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        //        }
        //        if (i === 6) {
        //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        //        }
        //        if (i === 8) {
        //        $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        //        }
        //
        //        });
        //        $(this).parents("tr").find(".add-sale, .edit-sale").toggle();
        //        $(".add-item-sale").attr("disabled", "disabled");
        //      });
        //
        //
        //      // Delete row on delete button click
        //        $(document).on("click", ".delete-sale", function(){
        //          var row =  $(this).closest('tr');
        //          var siblings = row.siblings();
        //          siblings.each(function(index) {
        //          $(this).children('td').first().text(index + 1);
        //          });
        //          $(this).parents("tr").remove();
        //
        //        });
        //
        //
        //        $('#new-sale-submit').on('submit',function(e){
        //        e.preventDefault();
        //        var table = $('#new-sale-table');
        //        var data = [];
        //        var sale_id = $('#sale_id').val();
        //        var customer = $('#customer').val();
        //        var payment_method = $('#payment_method').val();
        //        var footer_desc = $('#footer_desc').val();
        //
        //        table.find('tr').each(function (i, el){
        //          if(i != 0)
        //          {
        //            var $tds = $(this).find('td');
        //            var row = {
        //              'item_code' : "",
        //              'item_name' : "",
        //              'description' : "",
        //              'width' : "",
        //              'height' : "",
        //              'unit' : "",
        //              'qty' : "",
        //              'rate' : "",
        //            };
        //            $tds.each(function(i, el){
        //              if (i === 1) {
        //                  row["item_code"] = ($(this).text());
        //              }
        //              if (i === 2) {
        //                  row["item_name"] = ($(this).text());
        //              }
        //              else if (i === 3) {
        //                  row["description"] = ($(this).text());
        //              }
        //              else if (i === 4) {
        //                  row["width"] = ($(this).text());
        //              }
        //              else if (i === 5) {
        //                  row["height"] = ($(this).text());
        //              }
        //              else if (i === 6) {
        //                  row["unit"] = ($(this).text());
        //              }
        //              else if (i === 8) {
        //                  row["qty"] = ($(this).text());
        //              }
        //              else if (i === 9) {
        //                  row["rate"] = ($(this).text());
        //              }
        //            });
        //            data.push(row);
        //          }
        //        });
        //
        //           req =	$.ajax({
        //              headers: { "X-CSRFToken": getCookie("csrftoken") },
        //              type: 'POST',
        //              url : '/transaction/sale/new/',
        //              data:{
        //                'sale_id': sale_id,
        //                'customer': customer,
        //                'payment_method': payment_method,
        //                'footer_desc': footer_desc,
        //                'items': JSON.stringify(data),
        //              },
        //              dataType: 'json'
        //            })
        //            .done(function done(){
        //              alert("Sales Created");
        //              location.reload();
        //            })
        //      });


})
