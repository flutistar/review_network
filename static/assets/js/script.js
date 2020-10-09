$(function() {
    var customer_ip;
    $.getJSON('http://gd.geobytes.com/GetCityDetails?callback=?', function(data) {
        customer_ip = data['geobytesipaddress'];
    });
    var owner = $('#owner');
    var cardNumber = $('#cardNumber');
    var cardNumberField = $('#card-number-field');
    var CVV = $("#cvv");
    var mastercard = $("#mastercard");
    var confirmButton = $('#confirm-purchase');
    var visa = $("#visa");
    var amex = $("#amex");

    // Use the payform library to format and validate
    // the payment fields.

    cardNumber.payform('formatCardNumber');
    CVV.payform('formatCardCVC');

    cardNumber.keyup(function() {

        amex.removeClass('transparent');
        visa.removeClass('transparent');
        mastercard.removeClass('transparent');

        if ($.payform.validateCardNumber(cardNumber.val()) == false) {
            cardNumberField.addClass('has-error');
        } else {
            cardNumberField.removeClass('has-error');
            cardNumberField.addClass('has-success');
        }

        if ($.payform.parseCardType(cardNumber.val()) == 'visa') {
            mastercard.addClass('transparent');
            amex.addClass('transparent');
        } else if ($.payform.parseCardType(cardNumber.val()) == 'amex') {
            mastercard.addClass('transparent');
            visa.addClass('transparent');
        } else if ($.payform.parseCardType(cardNumber.val()) == 'mastercard') {
            amex.addClass('transparent');
            visa.addClass('transparent');
        }
    });

    confirmButton.click(function(e) {

        e.preventDefault();
        var date = new Date();
        var current_month = date.getMonth();
        var current_year = date.getFullYear();
        var expire_month = $('#expiration-month').val();
        var expire_year = $('#expiration-year').val();
        var amount = $('#amount').val();
        var isCardValid = $.payform.validateCardNumber(cardNumber.val());
        var isCvvValid = $.payform.validateCardCVC(CVV.val());
        if(owner.val().length < 5){
            $("#error_message").html('<i class="fas fa-exclamation-circle"></i> Please enter the correct owner name');
        } else if (!isCardValid) {
            $("#error_message").html('<i class="fas fa-exclamation-circle"></i> Please enter the correct card number');
        } else if (!isCvvValid) {
            $("#error_message").html('<i class="fas fa-exclamation-circle"></i> The CVV is not valid.');
        } else if (expire_month<current_month && expire_year<=current_year) {
            $("#error_message").html('<i class="fas fa-exclamation-circle"></i> Please select the correct dxpiration date.');
        } else {
            $("#error_message").html('');
            confirmButton.prop('disabled', true);
            var holder_name = owner.val();
            var card_number = cardNumber.val();
            var cvv_value = CVV.val();
            var order_id = $("#order_id").val();
            var crsf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
            var url = "/payout/confirm/";
            $.ajax({
                type: "POST",
                url: url,
                data: {
                    amount: amount,
                    customer_ip: customer_ip,
                    holder_name: holder_name,
                    card_number: card_number,
                    cvv: cvv_value,
                    expire_month: expire_month,
                    expire_year: expire_year,
                    order_id: order_id,
                    csrfmiddlewaretoken: crsf_token,
                },
                success: function (response)
                {
                    if(response == 'Success'){
                        $("#credit_card_form").css('display', 'none');
                        $("#thank_you_form").css('display', 'block');
                    }
                    else{
                        alert(response);
                    }
                    
                }
            });
            return false;

        }
    });
});
