$(function () {
    //点击小图标播放
    var plybtn = $('.plybtn');
    plybtn.click(littlebtn);

    function littlebtn() {
        var thisbtn = $(this);
        var src = thisbtn.prev().html();
        var songname = thisbtn.parent().next().html();
        var singer = thisbtn.parent().next().next().next().children().html();
        var duration = thisbtn.parent().next().next().html();
        var $li = $('<li class="templi"  playing="1"><div class="temp3"><div class="tempsongname">'+songname+'</div><div class="tempsongurl">'+src+'</div><div class=\"tempsinger\">'+singer+'</div><div class=\"tempduration\">'+duration+'</div></div><div class="tempsongdel"></div></li>');
        var lis = $('.tempul')[0].children;
        if(lis.length>0){
            if(notexists(lis,$li)){
                $('.tempul').append($li);
            }
        }else {
            $('.tempul').append($li);
        }

        $('#playing').attr({'src':src});
        $('#playing')[0].play();
        $('.songname').html(songname);
        $('.singer').html(singer);
        timer = setInterval(ProgressTime,1000);
        plybtn.removeClass('rspbaction');
        thisbtn.addClass('rspbaction');


        $('#playing')[0].addEventListener('error',function () {
            this.load();
        });
        $('#playing')[0].addEventListener('canplay',function () {
            this.play();
        });
        $('#playing')[0].addEventListener('ended',function () {
            thisbtn.removeClass('rspbaction');
        });


    }


    //搜索结果div高度
    var resheight;
    if($('#netease').height()>$('#qq').height()){
        resheight = $('#netease').height();
    }else{
        resheight = $('#qq').height();
    }
    $('.rstmain').height(resheight+150);


    //结果中点击歌手名 以该名字再次搜索
    $('.srchsinger').click(function () {
        $.ajax({
            url:'/search?s='+$(this).html(),
            type:'get',
            success:function (resText) {
                $('.main').html(resText)
            }
        })
    });

    $('.addlstbtn').click(function () {
        thisaddbtn = $(this);
        $.ajax({
            type : 'GET',
            url : '/addsong/',
            success:function (data) {
                if(data=='请您先登录账号 才可使用歌单功能'){
                    alert(data)
                }
                else{
                    $('.addlistol').empty();
                    data = JSON.parse(data);
                    for(var i=0;i<data.length;i++){
                        var $li = $('<li class="addlistli">'+ data[i] +'</li>');
                        $('.addlistol').append($li)
                    }
                    $('#addlistmenu').css('visibility','visible')
                }
            }
         })
    });

    $('.addlistol').on('click','.addlistli',function () {
        $.ajax({
            type : 'POST',
            url:'/addsong/',
            data:{
                // csrfmiddlewaretoken:$('.csrf').html(),
                songlist_name:$(this).html(),
                songurl:thisaddbtn.prev().prev().html(),
                songname:thisaddbtn.parent().next().html(),
                singer:thisaddbtn.parent().next().next().next().children(".srchsinger").html(),
                duration:thisaddbtn.parent().next().next().html(),
            },
            success:function (resText) {
                $('#addlistmenu').css('visibility','hidden');
            }
        })
    });

});