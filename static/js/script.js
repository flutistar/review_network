(function($) {

    "use strict";

    function setImageHeight(){
        // Change the width of the div
        var $image_div = $(".screenshots");
        var width = $image_div.width();
        var height = width * 2 / 3;
        $image_div.height(height);
    }
    /*--------------------------------
        Upload screenshot
    ---------------------------------*/
    $('#id_image').on("change", function(){
        
        const previewContainer = document.getElementById('image_preview');
        const previewImage = previewContainer.querySelector('.image-preview__image');
        const previewDefaultText = previewContainer.querySelector('.image-preview__text');
        const file = this.files[0];
        if(file){
            const reader = new FileReader();
            previewDefaultText.style.display = 'none';
            previewImage.style.display = 'block';
            $('#image-upload-btn').prop('disabled', false);
            reader.addEventListener("load", function() {
                previewImage.setAttribute("src", this.result);
            });
            reader.readAsDataURL(file);
        } else {
            previewDefaultText.style.display = null;
            previewImage.style.display = null;
            $('#image-upload-btn').prop('disabled', true);
            previewImage.setAttribute("src", "");
        }
    });

    /*--------------------------------
        Submit Payment method
    ---------------------------------*/
    $('#payment_submit_btn').on('click', function(e){
        if (!e.isDefaultPrevented()){
            var bitcoin = $('#bitcoin_address').val();
            var order_notification = $('#order_notification')[0].checked;
            var crsf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
            var url = "/payment_update/";
            var old_n_value = $('#notification').val();
            if(old_n_value == 'False'){
                old_n_value = false;
            }else{
                old_n_value = true;
            }
            var old_b_value = $('#bitcoin').val();
            if(bitcoin == old_b_value && order_notification == old_n_value){
                return false;
            }
            if(bitcoin == ''){
                $("#danger-alert").fadeTo(2000, 1000).slideUp(1000, function() {
                    $("#danger-alert").slideUp(1000);
                });
                $('#bitcoin_address').focus();
                return false;
            }            
            // $('#bitcoin_address').val('');
            $('#bitcoin_address').focus();
            $.ajax({
                type: "POST",
                url: url,
                data: {
                    bitcoin_address: bitcoin,
                    csrfmiddlewaretoken: crsf_token,
                    order_notification, order_notification
                },
                success: function (response)
                {
                    if(response == 'Success'){
                        $("#success-alert").fadeTo(2000, 1000).slideUp(1000, function() {
                            $("#success-alert").slideUp(1000);
                        });
                    }
                    else{
                        $("#danger-alert").fadeTo(2000, 1000).slideUp(1000, function() {
                            $("#danger-alert").slideUp(1000);
                        });
                    }
                    
                }
            });
            return false;
        }
    });
    if(('.sign_up_form').length){
        $('#id_password1').attr('autocomplete', 'new-password');
    }
    /*--------------------------------
        Submit Registration Form
    ---------------------------------*/
    $('#registration_form').on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var url = "/account/register/";
            var data = $(this).serialize();
            $('.buttonload i').css('display', 'inline-block');
            $(".buttonload").prop('disabled', true); 
            $.ajax({
                type: "POST",
                url: url,
                data: data,
                success: function (data) {
                    // If Signup successful
                    if(typeof(data) == 'string' && data == 'Signup successful'){
                        $('#registration_form').css('display', 'none');
                        $('#signup_success').css('display','block');
                    }
                    // If failed signup function
                    if(typeof(data) == 'object'){
                        $('.buttonload i').css('display', 'none');
                        $(".buttonload").prop('disabled', false);
                        // Display all the error messages for each form field
                        $( ".error-container" ).remove();
                        for(var error in data){
                            var id = '#id_' + error;
                            var parent = $(id).parents('.form-element');
                            var html = "<div class='error-container'><div class='col col-sm-5'></div><div class='error-massage col col-sm-7'><p>" + data[error] + "</p></div></div>";
                            parent.append(html);
                        }
                    }
                    
                }
            });
            return false;
        }
    })
 
    /*--------------------------------
        Submit Order Function
    ---------------------------------*/
    $('#order_form').on('submit', function (e) {
        // if the validator does not prevent form submit
        if (!e.isDefaultPrevented()) {
            var url = "/manage/order_create/";
            var data = $(this).serialize();
            
            $('#order_form')[0].reset();
            $('#platform').focus();
            $("#order_submit i").css('display', 'inline-block');
            $("#order_submit").prop('disabled', true); 

            $.ajax({
                type: "POST",
                url: url,
                data: data,
                success: function (response)
                {
                    $('#order_submit i').css('display', 'none');
                    $("#order_submit").prop('disabled', false);
                    if(response == 'Success.'){
                        $("#success-alert").fadeTo(2000, 1000).slideUp(1000, function() {
                            $("#success-alert").slideUp(1000);
                        });
                    }
                    else{
                        $("#danger-alert").html('<button type="button" class="close" data-dismiss="alert">x</button><strong>Error! </strong> ' + response);
                        $("#danger-alert").fadeTo(2000, 1000).slideUp(1000, function() {
                            $("#danger-alert").slideUp(1000);
                        });
                    }
                }
            });
            return false;
        }
    })

    $("#img_modal").on('show.bs.modal', function(event) {
        var $modal = $(this);
        var $target_div = $(event.relatedTarget);
        if($target_div.parents('.product_screenshots').length){
            var page = 'product';
        }else{
            var page = 'review';
        }
        var task_id = $target_div.data('task_id');
        var url = "/manage/screenshot_popup_modal?task_id=" + task_id + "&page=" + page;
        $.ajax({
            type: "GET",
            url: url,
            success: function (data)
            {
                if(data != 'Failed'){
                    var $img = $("<img  src='" + data + "'>");
                    $modal.find('.modal-title').text(task_id);
                    $modal.find('.modal-image-preview').empty().append($img);
                }
                
            }
        });
    }); 

    /*--------------------------------
        Approve review screenshot
    ---------------------------------*/
    $('.approve_screenshot').on('click', function(event){
        console.log(event);
        var task_id = $(this).data('task_id');
        var url = "/manage/approve_screenshot?task_id=" + task_id;
        $.ajax({
            type: "GET",
            url: url,
            success: function (data)
            {
                if(data != 'Failed'){
                    var $review_img_div = $('#screenshot_' + task_id);
                    // $review_img_div.css('display', 'none');
                    $review_img_div.remove();
                    var $text = "<strong>Success! </strong> You approved a task successfully";
                    $('#success-alert').find('.alert_text').append($text);
                    $("#success-alert").fadeTo(5000, 1000).slideUp(1000, function() {
                        $("#success-alert").slideUp(1000);
                    });
                }
                return true;
            }
        });
    });

    /*--------------------------------
        Approve review screenshot
    ---------------------------------*/
    $('.reject_screenshot').on('click', function(event){
        console.log($(this));
        var task_id = $(this).data('task_id');
        var reject_text = $('#reject_text').val()
        if (!(reject_text)){
            alert("Please input the reject text");
            return true;
        }
        var crsf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        var url = "/manage/reject_screenshot/?task_id=" + task_id;
        $.ajax({
            type: "POST",
            url: url,
            data: {
                task_id: task_id,
                reject_text: reject_text,
                csrfmiddlewaretoken: crsf_token,
            },
            success: function (data)
            {
                if(data != 'Failed'){
                    var $review_img_div = $('#screenshot_' + task_id);
                    // $review_img_div.css('display', 'none');
                    $review_img_div.remove();
                    var $text = "<strong>Success! </strong> You rejected a task.";
                    $('#success-alert').find('.alert_text').append($text);
                    $("#success-alert").fadeTo(5000, 1000).slideUp(1000, function() {
                        $("#success-alert").slideUp(1000);
                    });
                    return true;
                }
            }
        });
    });


    /*------------------------------------------
        = FUNCTIONS
    -------------------------------------------*/
    // Toggle mobile navigation
    function toggleMobileNavigation() {
        var navbar = $("#navbar");
        var openBtn = $(".navbar-header .open-btn");
        var closeBtn = $("#navbar .close-navbar");
        var navLinks = $("#navbar > ul > li > a");

        openBtn.on("click", function() {
            if (!navbar.hasClass("slideInn")) {
                navbar.addClass("slideInn");
            }
            return false;
        })

        closeBtn.on("click", function() {
            if (navbar.hasClass("slideInn")) {
                navbar.removeClass("slideInn");
            }
            return false;            
        })
        
        navLinks.on("click", function() {
            if (navbar.hasClass("slideInn")) {
                navbar.removeClass("slideInn");
            }
            // return false;            
        })
    }

    toggleMobileNavigation();

    /*------------------------------------------
        = STICKY HEADER
    -------------------------------------------*/
    function stickyHeader() {
        if ($(".site-header").length) {
            var navigation = $(".site-header > .navigation"),
                scroll = $(window).scrollTop(),
                top = $(".site-header > .topbar").height();

            if (scroll > top) {
                navigation.addClass("sticky");
            } else {
                navigation.removeClass("sticky");
            }
        }
    }

    // Architect home sticky header
    function stickyHeaderArchitect() {
        if ($(".architect-header").length) {
            var navigation = $(".architect-header > .navigation"),
                scroll = $(window).scrollTop(),
                top = $(".architect-header .navigation").height();

            if (scroll > top) {
                navigation.addClass("sticky");
            } else {
                navigation.removeClass("sticky");
            }       
        }
    }

    // Events home sticky header
    function stickyHeaderEvents() {
        if ($(".events-header").length) {
            var navigation = $(".events-header > .navigation");
            var scroll = $(window).scrollTop();
            var top = $(".events-header .navigation").height();

            if (scroll > top) {
                navigation.addClass("sticky");
            } else {
                navigation.removeClass("sticky");
            }

        }
    }


    /*------------------------------------------
        = POPUP VIDEO
    -------------------------------------------*/  
    if ($(".video-btn").length) {
        $(".video-btn").on("click", function(){
            $.fancybox({
                href: this.href,
                type: $(this).data("type"),
                'title'         : this.title,
                helpers     : {  
                    title : { type : 'inside' },
                    media : {}
                },

                beforeShow : function(){
                    $(".fancybox-wrap").addClass("gallery-fancybox");
                }
            });
            return false
        });    
    }


    /*------------------------------------------
        = SERVICES STYLE 2 SLIDER
    -------------------------------------------*/
    if ($(".services-s3-slider").length) {
        $(".services-s3-slider").owlCarousel({
            autoplay:true,
            smartSpeed: 100,
            stagePadding: 10,
            slideBy: 1,
            margin: 30,
            autoplayHoverPause:true,
            mouseDrag: false,
            loop: true,
            responsive: {
                0 : {
                    items: 1
                },

                600 : {
                    items: 2
                },

                992 : {
                    items: 3
                }
            }
        });
    }

    /*--------------------------------------------------
        = HOSTING PAGE UPLOAD DOWNLOAD PROGRESS BAR
    --------------------------------------------------*/
    function uploadDownloadProgress() {
        if ($(".progress-bar2").length) {
            var $progress_bar = $('.progress-bar2');
            $progress_bar.appear();
            $(document.body).on('appear', '.progress-bar2', function() {
                var current_item = $(this);
                if (!current_item.hasClass('appeared')) {
                    var percent = current_item.data('percent');
                    current_item.append('<span>' + percent + '%' + '</span>').css('width', percent + '%').addClass('appeared');
                }
                
            });
        };
    }

    uploadDownloadProgress();



    // function modalPopUp(){
    //     $(".box-inner").on('click', function(){
    //         var img_id = $(this).find("img")[0].id;
    //         var src = "{% static 'images/tasks/" + img_id + ".png' %}";
    //         var $modal_body = $('.modal-body')[0];
    //         $modal_body.append("<img src='" + src + "'>");
    //     });
    // }
    // modalPopUp();

    /*==========================================================================
        WHEN WINDOW SCROLL
    ==========================================================================*/
    $(window).on("load", function() {
        setImageHeight();
    });
    $( window ).bind("resize", function(){
        setImageHeight();
    });
    $(window).on("scroll", function() {

        stickyHeader();

        stickyHeaderArchitect();

        stickyHeaderEvents();

    });
})(window.jQuery);