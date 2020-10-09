if (!$) {
    // Need this line because Django also provided jQuery and namespaced as django.jQuery
    $ = django.jQuery;
}

$(document).ready(function() {
    $('#order_form').on('submit', function(e){
        if (!e.isDefaultPrevented()) {
            var url = "/manage/update_order/";
            var id = $('.readonly').text();
            var paid = $('#id_paid')[0].checked;
            var data = $(this).serialize() + '&id=' + id;  
            if (paid == false){
                data += '&paid=off';
            }            
            $.ajax({
                type: "POST",
                url: url,
                data: data,
                success: function (response)
                {
                    console.log(response);
                }
            });
        }
    });
});

