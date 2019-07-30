$(function () {

    //搜索结果div高度
    var resheight = [$('#netease').height(),$('#qq').height(),$('#kuwo').height()].reduce((prev,cur)=>Math.max(prev,cur));
    $('.rstmain').height(resheight+150);
    

    // $('.main').on('click','.plybtn',littlebtn);
    //
    // function littlebtn() {
    //     var thisbtn = $(this);
    //     if(thisaddbtn.prev().html().length<30){
    //         var strs = thisaddbtn.prev().html();
    //         strs = strs.split("|");
    //         console.log(strs);
    //         $.ajax({
    //             async:false,
    //             type:'POST',
    //             url:'/geturl/',
    //             data:{
    //                 songid: strs[0],
    //                 source: strs[1]
    //             },
    //             success:function (data) {
    //                 thisaddbtn.prev().prev().html(data);
    //             }
    //         });
    //     }
    //
    //     var src = thisbtn.prev().html();
    //     var songname = thisbtn.parent().next().html();
    //     var singer = thisbtn.parent().next().next().next().children().html();
    //     var duration = thisbtn.parent().next().next().html();
    //     var $li = $('<li class="templi"  playing="1"><div class="temp3"><div class="tempsongname">'+songname+'</div><div class="tempsongurl">'+src+'</div><div class=\"tempsinger\">'+singer+'</div><div class=\"tempduration\">'+duration+'</div></div><div class="tempsongdel"></div></li>');
    //     var lis = $('.tempul')[0].children;
    //     if(lis.length>0){
    //         if(notexists(lis,$li)){
    //             $('.tempul').append($li);
    //         }
    //     }else {
    //         $('.tempul').append($li);
    //     }
    //
    //     $('#playing').attr({'src':src});
    //     $('#playing')[0].play();
    //     $('.songname').html(songname);
    //     $('.singer').html(singer);
    //     timer = setInterval(ProgressTime,1000);
    //     $('.plybtn').removeClass('rspbaction');
    //     thisbtn.addClass('rspbaction');
    //
    //     $('#playing')[0].addEventListener('ended',function () {
    //         thisbtn.removeClass('rspbaction');
    //     });
    //
    //
    // }



    // $('.main').on('click','.addlstbtn',function () {
    //     thisaddbtn = $(this);
    //     if(thisaddbtn.prev().prev().html().length<30){
    //         var strs = thisaddbtn.prev().prev().html();
    //         strs = strs.split("|");
    //         console.log(strs);
    //         $.ajax({
    //             async:false,
    //             type:'POST',
    //             url:'/geturl/',
    //             data:{
    //                 songid: strs[0],
    //                 source: strs[1]
    //             },
    //             success:function (data) {
    //                 thisaddbtn.prev().prev().html(data);
    //             }
    //         });
    //     }
    //     $.ajax({
    //         type : 'GET',
    //         url : '/addsong/',
    //         success:function (data) {
    //             if(data=='请您先登录账号 才可使用歌单功能'){
    //                 alert(data)
    //             }
    //             else{
    //                 $('.addlistol').empty();
    //                 data = JSON.parse(data);
    //                 for(var i=0;i<data.length;i++){
    //                     var $li = $('<li class="addlistli">'+ data[i] +'</li>');
    //                     $('.addlistol').append($li)
    //                 }
    //                 $('#addlistmenu').css('visibility','visible')
    //             }
    //         }
    //      })
    // });

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