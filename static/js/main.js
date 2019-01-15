$(function(){
    var playing = false;
    var timer;
    var totlong = $('.barbg')[0].offsetWidth - 7;   //进度条总长度  totlong
    var isMute = false;
    var playmode = 1; // 1列表循环 2随机播放 3单曲循环
    var i;            //给hash赋值用

    // 监听audio状态获取歌曲总时长    后加页面的时间显示
    $('#playing')[0].addEventListener('canplay',function () {
        totaltime = $('#playing')[0].duration; // 不为全局变量会有问题
        inhtml_totaltime = secFormat(totaltime);
        inhtml_currtime = secFormat($('#playing')[0].currentTime); //时间显示
        $('.currtime').html(inhtml_currtime+"/"+inhtml_totaltime);
    });

    $('#playing')[0].addEventListener('playing',function () {
        playing = true;
        $('.btns .play').addClass('pause').removeClass('play');
    });

    // 歌曲播放完毕后的操作 按钮变化及判断播放模式及处理
    $('#playing')[0].addEventListener('ended',function(){
        clearInterval(timer);
        var pausebtn = document.getElementsByClassName('pause')[0];
        if(pausebtn){
            pausebtn.setAttribute('class','play');
        }
        playing = false;
        if(playmode==1){
            var lis = $('.tempul')[0].children;
            for(var i=0;i<lis.length;i++){
                if(lis[i].children[0].children[1].innerHTML == $('#playing')[0].getAttribute('src')){
                    if(lis[i+1]){
                        var tsrc = lis[i+1].children[0].children[1].innerHTML;
                        var tsongname = lis[i+1].children[0].children[0].innerHTML;
                        var tsinger = lis[i+1].children[0].children[2].innerHTML;
                        $('#playing').attr({'src':tsrc});
                        $('#playing')[0].play();
                        $('.songname').html(tsongname);
                        $('.singer').html(tsinger);
                        $('.plybtn').removeClass('rspbaction');
                        timer = setInterval(ProgressTime,1000);
                        break;
                    }else{
                        var tsrc = lis[0].children[0].children[1].innerHTML;
                        var tsongname = lis[0].children[0].children[0].innerHTML;
                        var tsinger = lis[0].children[0].children[2].innerHTML;
                        $('#playing').attr({'src':tsrc});
                        $('#playing')[0].play();
                        $('.songname').html(tsongname);
                        $('.singer').html(tsinger);
                        $('.plybtn').removeClass('rspbaction');
                        timer = setInterval(ProgressTime,1000);
                    }

                }
            }
        }
        else if(playmode==2){
            var lis = $('.tempul')[0].children;
            var tempindex = parseInt(Math.random() * lis.length);
            var tsrc = lis[tempindex].children[0].children[1].innerHTML;
            var tsongname = lis[tempindex].children[0].children[0].innerHTML;
            var tsinger = lis[tempindex].children[0].children[2].innerHTML;
            if(lis.length==1){
                $('#playing').attr({'src':tsrc});
                $('#playing')[0].play();
                $('.songname').html(tsongname);
                $('.singer').html(tsinger);
                $('.plybtn').removeClass('rspbaction');
                timer = setInterval(ProgressTime,1000);
            }
            else{
                if(tsrc==$('#playing').attr('src')){                    //防止随机的还是同一首歌
                    tempindex++;
                    if(tempindex==lis.length){                          //防止索引超出范围
                        tempindex -= 2;
                    }
                    tsrc = lis[tempindex].children[0].children[1].innerHTML;
                    tsongname = lis[tempindex].children[0].children[0].innerHTML;
                    tsinger = lis[tempindex].children[0].children[2].innerHTML;
                }
            }
            $('#playing').attr({'src':tsrc});
            $('#playing')[0].play();
            $('.songname').html(tsongname);
            $('.singer').html(tsinger);
            $('.plybtn').removeClass('rspbaction');
            timer = setInterval(ProgressTime,1000);
        }
    });

    $('.btns .play').click(function(){
        if(playing){
            $('#playing')[0].pause();  //点击暂停
            $(this).addClass('play').removeClass('pause');
            clearInterval(timer);
        }else{
            $('#playing')[0].play();    //点击播放
            // $(this).addClass('pause').removeClass('play');
            timer = setInterval(ProgressTime,1000);
        }
        playing = !playing;
    });



    // 如果循环导致按钮错乱 可给#playing增加事件监听 paused
    ProgressTime = function(){
        var currtime = $('#playing')[0].currentTime; //audio当前播放的时间 currtime  秒
        var currwidthscale = currtime / totaltime;   //当前播放比例
        var currwidth = currwidthscale * totlong;    //当前偏移量
        $('.curbtn')[0].style.marginLeft = parseInt(currwidth) + 'px';  //进度小圆点移动
        $('.cur')[0].style.width =  currwidth + 'px';   //红色进度条跟随
        //播放时间更新
        inhtml_currtime = secFormat($('#playing')[0].currentTime);
        $('.currtime').html(inhtml_currtime+"/"+inhtml_totaltime);
    };


    // 进度条可拖拽控制播放进度 （根据偏移量求currtime）
    // 先让鼠标和进度条 可以拖拽
    $('.curbtn')[0].onmousedown = function(){
        document.onmousemove = function(evt){
            $(':not()').css('pointer-events', 'none');       //防止拖拽选中其他元素造成bug
            var mousex =  evt.clientX;  // 鼠标按下的X位置
            // 通过两个offsetLeft相加 获取barbg距离窗口的距离 布局导致需要相加获取 有时间再调
            var targetx = mousex - ($('.barbg')[0].offsetParent.offsetLeft + $('.song')[0].offsetLeft)
            - 4;
            $('.curbtn')[0].style.marginLeft = targetx + 'px';
            $('.cur')[0].style.width = targetx + 'px';
            // 求目标比例 算目标时间
            var targetscale = targetx / totlong;  //播放比例
            var targettime = targetscale * totaltime; //目标时间
            $('#playing')[0].currentTime = targettime;
            ProgressTime()
        };
        document.onmouseup = function(){
            $(':not()').css('pointer-events', 'auto');
            this.onmousedown = null;
            this.onmousemove = null;
        }
    };

    // 点击整个进度条某点切换进度
    $('.barbg')[0].onmousedown = function(evt){
        var mousex = evt.clientX;
            var targetx = mousex - ($('.barbg')[0].offsetParent.offsetLeft + $('.song')[0].offsetLeft)
            -1;
            $('.curbtn')[0].style.marginLeft = targetx + 'px';
            $('.cur')[0].style.width = targetx + 'px';
            var targetscale = targetx / totlong;  //播放比例
            var targettime = targetscale * totaltime; //目标时间
            $('#playing')[0].currentTime = targettime;
            ProgressTime()
        };

    // 音量控制条功能
    $('.volbtn')[0].onmousedown = function(){
        document.onmousemove = function(evt){
            volctrl(evt);
            $(':not()').css('pointer-events', 'none');
            document.onmouseup = function(){
                $(':not()').css('pointer-events', 'auto');
                this.onmousedown = null;
                this.onmousemove = null;
            }
        }
    };
    $('.volbar')[0].onmousedown = function(evt){
        volctrl(evt)
    };

    // 静音相关
    //音量条静音
    $('#playing')[0].addEventListener('volumechange',function(){
        if(this.volume==0){
            $('#mutebtn').addClass('muteactive').removeClass('mute');
            isMute = true;
        }else{
            $('#mutebtn').removeClass('muteactive').addClass('mute');
            isMute = false;
        }
    });
    //小喇叭静音开关
    var volvalue;
    var pxval;
    $('#mutebtn').click(function(){
    if(isMute){
        $('#playing')[0].volume = volvalue;
        $('.volbtn')[0].style.marginLeft = pxval + 'px';
        $('.volcur')[0].style.width = pxval + 'px';
    }else{
        volvalue = $('#playing')[0].volume;
        pxval = volvalue*100;
        $('#playing')[0].volume = 0;
        $('.volbtn')[0].style.marginLeft = 0 + 'px';
        $('.volcur')[0].style.width = 0 + 'px';
    }
});

    // 登录注册框的显示与取消
    $('.top-links').on('click','#login',function(){
        $('.container').addClass('blur');
        $('.loginbg').fadeIn();
        $('.login').fadeIn();
    });
    $('#logquit').click(function(){
        $('.container').removeClass('blur');
        $('.loginbg').fadeOut();
        $('.login').fadeOut();
    });
    $('.top-links').on('click','#register',function(){
        $('.container').addClass('blur');
        $('.loginbg').fadeIn();
        $('.register').fadeIn();
    });
    $('#regquit').click(function(){
        $('.container').removeClass('blur');
        $('.loginbg').fadeOut();
        $('.register').fadeOut();
    });

    //窗口宽度变化更换主页面背景图片
    $(window).resize(function(){
        if(document.body.clientWidth>1920){
            $('.tu2').attr('src',"/static/img/tyt2560.png");
            $('.tu1').attr('src','/static/img/qx2560.png');
            $('.bgbanner img').width(2560)
        }
        if(document.body.clientWidth<1920){
            $('.tu2').attr('src',"/static/img/tyt1920.png");
            $('.tu1').attr('src','/static/img/qx1920.png');
            $('.bgbanner img').width(1920)

        }
    });

    //首页背景图轮播
    var banindex = 0;
    setInterval(function(){
        if(banindex>1){
            banindex = 0;
        }
        $('.bgbanner li').eq(banindex).fadeIn().siblings().fadeOut();
        banindex++;
    },15000);


    // 搜索五连
    function mainSearch(){
        var s = $('.srchinput').val();
        if(!$.trim(s)){
            return
        }
        i = $('.srchinput').val();
        location.hash = i;

    }

    function topSearch(){
        var s = $('.topsrchipt').val();
        if(!$.trim(s)){
            return
        }
        i = $('.topsrchipt').val();
        location.hash = i;

    }


    $('.srchbtn').click(mainSearch);
    $('.srchinput').bind('keyup',function (evt) {
        if(evt.keyCode=="13"){
            mainSearch();
        }
    });
    $('.top-links').on('click','.topsrchbtn',topSearch);
    $('.top-links').bind('keyup','.topsrchipt',function (evt) {
        if(evt.keyCode=="13"){
            topSearch();
        }
    });

    // 播放列表相关
    var templistshow = false;
    $('.playlist').click(function () {
        if (templistshow) {
            $('.templist').css('display','none');
        }else{
            $('.templist').css('display','block');
        }
        templistshow = !templistshow;
    });


    $('.tempdel').click(function () {
        $('.tempul').empty();
    });

    $('.tempclose').click(function () {
        $('.templist').css('display','none');
        templistshow = false;
    });

    $('.tempul').on('click','.tempsongdel',function () {
        $(this).parent().remove();
    });

    $('.tempul').on('click','.temp3',function () {
        var tsrc = $(this).children()[1].innerHTML;
        var tsongname = $(this).children()[0].innerHTML;
        var tsinger = $(this).children()[2].innerHTML;
        $('#playing').attr({'src':tsrc});
        $('#playing')[0].play();
        $('.songname').html(tsongname);
        $('.singer').html(tsinger);
        $('.plybtn').removeClass('rspbaction');
        timer = setInterval(ProgressTime,1000);

    });

    // 循环模式相关
    $('.loop').click(function () {
        if(playmode==1){
            playmode = 2;
            $('#playing').removeAttr('loop');
            $(this).attr('title','随机播放');
            $(this).css('background-image','url(/static/img/shuffle-g.png)');
        }
        else if(playmode==2){
            playmode = 3;
            $('#playing').attr('loop','true');
            $(this).attr('title','单曲循环');
            $(this).css('background-image','url(/static/img/single-g.png)');
        }
        else{
            playmode = 1;
            $('#playing').removeAttr('loop');
            $(this).attr('title','列表循环');
            $(this).css('background-image','url(/static/img/loop-g.png)');
        }
    });

    $('.loop').hover(function () {
        if(playmode==1){
            $(this).css('background-image','url(/static/img/loop-r.png)');
        }
        else if(playmode==2){
            $(this).css('background-image','url(/static/img/shuffle-r.png)');
        }
        else{
            $(this).css('background-image','url(/static/img/single-r.png)');
        }
    },function () {
        if(playmode==1){
            $(this).css('background-image','url(/static/img/loop-g.png)');
        }
        else if(playmode==2){
            $(this).css('background-image','url(/static/img/shuffle-g.png)');
        }
        else {
            $(this).css('background-image','url(/static/img/single-g.png)');
        }
    });

    // next prev功能
    $('.next').click(function () {
        clearInterval(timer);
        var lis = $('.tempul')[0].children;
        if(playmode==1 || playmode==3){
            if(lis.length>0){
                for(var i=0;i<lis.length;i++){
                    if(lis[i].children[0].children[1].innerHTML == $('#playing')[0].getAttribute('src')){
                        if(lis[i+1]){
                            var tsrc = lis[i+1].children[0].children[1].innerHTML;
                            var tsongname = lis[i+1].children[0].children[0].innerHTML;
                            var tsinger = lis[i+1].children[0].children[2].innerHTML;
                            $('#playing').attr({'src':tsrc});
                            $('#playing')[0].play();
                            $('.songname').html(tsongname);
                            $('.singer').html(tsinger);
                            $('.plybtn').removeClass('rspbaction');
                            timer = setInterval(ProgressTime,1000);
                            break;
                        }else{
                            var tsrc = lis[0].children[0].children[1].innerHTML;
                            var tsongname = lis[0].children[0].children[0].innerHTML;
                            var tsinger = lis[0].children[0].children[2].innerHTML;
                            $('#playing').attr({'src':tsrc});
                            $('#playing')[0].play();
                            $('.songname').html(tsongname);
                            $('.singer').html(tsinger);
                            $('.plybtn').removeClass('rspbaction');
                            timer = setInterval(ProgressTime,1000);
                        }

                    }

                }
            }

        }
        else{
            var tempindex = parseInt(Math.random() * lis.length);
            var tsrc = lis[tempindex].children[0].children[1].innerHTML;
            var tsongname = lis[tempindex].children[0].children[0].innerHTML;
            var tsinger = lis[tempindex].children[0].children[2].innerHTML;
            if(lis.length==1){
                $('#playing').attr({'src':tsrc});
                $('#playing')[0].play();
                $('.songname').html(tsongname);
                $('.singer').html(tsinger);
                $('.plybtn').removeClass('rspbaction');
                timer = setInterval(ProgressTime,1000);
            }
            else{
                if(tsrc==$('#playing').attr('src')){                    //防止随机的还是同一首歌
                    tempindex++;
                    if(tempindex==lis.length){                          //防止索引超出范围
                        tempindex -= 2;
                    }
                    tsrc = lis[tempindex].children[0].children[1].innerHTML;
                    tsongname = lis[tempindex].children[0].children[0].innerHTML;
                    tsinger = lis[tempindex].children[0].children[2].innerHTML;
                }
            }
            $('#playing').attr({'src':tsrc});
            $('#playing')[0].play();
            $('.songname').html(tsongname);
            $('.singer').html(tsinger);
            $('.plybtn').removeClass('rspbaction');
            timer = setInterval(ProgressTime,1000);
        }

    });

    $('.prev').click(function () {
        clearInterval(timer);
        var lis = $('.tempul')[0].children;
        if(playmode==1 || playmode==3){
            if(lis.length>0){
                for(var i=0;i<lis.length;i++){
                    if(lis[i].children[0].children[1].innerHTML == $('#playing')[0].getAttribute('src')){
                        if(lis[i-1]){
                            var tsrc = lis[i-1].children[0].children[1].innerHTML;
                            var tsongname = lis[i-1].children[0].children[0].innerHTML;
                            var tsinger = lis[i-1].children[0].children[2].innerHTML;
                            $('#playing').attr({'src':tsrc});
                            $('#playing')[0].play();
                            $('.songname').html(tsongname);
                            $('.singer').html(tsinger);
                            $('.plybtn').removeClass('rspbaction');
                            timer = setInterval(ProgressTime,1000);
                            break;
                        }else{
                            var tsrc = $('.templi:last-child')[0].children[0].children[1].innerHTML;
                            var tsongname= $('.templi:last-child')[0].children[0].children[0].innerHTML;
                            var tsinger = $('.templi:last-child')[0].children[0].children[2].innerHTML;
                            $('#playing').attr({'src':tsrc});
                            $('#playing')[0].play();
                            $('.songname').html(tsongname);
                            $('.singer').html(tsinger);
                            $('.plybtn').removeClass('rspbaction');
                            timer = setInterval(ProgressTime,1000);
                            break;
                        }

                    }

                }
            }

        }
        else{
            var tempindex = parseInt(Math.random() * lis.length);
            var tsrc = lis[tempindex].children[0].children[1].innerHTML;
            var tsongname = lis[tempindex].children[0].children[0].innerHTML;
            var tsinger = lis[tempindex].children[0].children[2].innerHTML;
            if(lis.length==1){
                $('#playing').attr({'src':tsrc});
                $('#playing')[0].play();
                $('.songname').html(tsongname);
                $('.singer').html(tsinger);
                $('.plybtn').removeClass('rspbaction');
                timer = setInterval(ProgressTime,1000);
            }
            else{
                if(tsrc==$('#playing').attr('src')){                    //防止随机的还是同一首歌
                    tempindex++;
                    if(tempindex==lis.length){                          //防止索引超出范围
                        tempindex -= 2;
                    }
                    tsrc = lis[tempindex].children[0].children[1].innerHTML;
                    tsongname = lis[tempindex].children[0].children[0].innerHTML;
                    tsinger = lis[tempindex].children[0].children[2].innerHTML;
                }
            }
            $('#playing').attr({'src':tsrc});
            $('#playing')[0].play();
            $('.songname').html(tsongname);
            $('.singer').html(tsinger);
            $('.plybtn').removeClass('rspbaction');
            timer = setInterval(ProgressTime,1000);
        }


    });


    // 登陆注册
    var regcansub = false;
    $('#urname').blur(function () {
        if($(this).val()){
            $.ajax({
                type:'GET',
                url:"/user/register/",
                data:{username:$(this).val()},
                success:function (data) {
                    if (data=='该用户名可以使用') {
                        regcansub = true;
                    }
                    else {
                        regcansub = false;
                    }
                    $('#regcheckmsg').html(data);
                }
            })
        }
        else {
            $('#regcheckmsg').html('用户名不能为空');
            regcansub = false;

        }
    });

    $('#urpwd2').blur(function () {
        if($(this).val()!=$('#urpwd').val()){
            $('#regcheckmsg').html('两次密码输入不一致');
            regcansub = false;
        }
        else {
            $('#regcheckmsg').html('&#12288;');
            regcansub = true;
        }
    });

    $('#regsubmit').click(function () {
        if(regcansub){
            $.ajax({
                type:'POST',
                url:"/user/register/",
                data:{
                    username:$('#urname').val(),
                    userpwd:$('#urpwd').val(),
                    useremail:$('#uemail').val(),
                },
                success:function (data) {
                    if(data=='ok'){
                        $('.container').removeClass('blur');
                        $('.loginbg').fadeOut();
                        $('.register').fadeOut();
                        var username = $('#urname').val();
                        $('.top-links').html('<li id="srcli">\n<input type="text" class="topsrchipt" placeholder="搜索">\n<button class="topsrchbtn"></button>\n</li><a href="javascript:void(0);" id="mylist"><li>我的歌单</li></a>\n<a href="javascript:void(0);" id="logout"><li>退出</li></a>\n<li id="user">'+username+'</li>')
                    }
                    else {
                        $('#regcheckmsg').html(data);
                    }
                }
            })
        }
    });

    $('.top-links').on('click','#logout',function () {
        $.ajax({
            type:'GET',
            url:'/user/logout/',
            success:function (data) {
                $('.top-links').html('<li id="srcli">\n<input type="text" class="topsrchipt" placeholder="搜索">\n<button class="topsrchbtn"></button></li>\n<a href="javascript:void(0);" id="login"><li>登录</li></a>\n<a href="javascript:void(0);" id="register"><li id="registerli">注册账号</li></a>');
                location.hash = '';
                window.location.reload();
            }
        })
    });

    $('#logsubmit').click(function () {
        $.ajax({
            type:'POST',
            url:'/user/login/',
            data:{
                username : $('#uname').val(),
                upwd : $('#upwd').val(),
                issave: $('#issave').prop('checked'),     //用此方法查看是否被选中 而val()取值永远固定
            },
            success: function (data) {
                if(data=='ok'){
                    $('.container').removeClass('blur');
                    $('.loginbg').fadeOut();
                    $('.login').fadeOut();
                    var username = $('#uname').val();
                    $('.top-links').html('<li id="srcli">\n<input type="text" class="topsrchipt" placeholder="搜索">\n<button class="topsrchbtn"></button>\n</li><a href="javascript:void(0);" id="mylist"><li>我的歌单</li></a>\n<a href="javascript:void(0);" id="logout"><li>退出</li></a>\n<li id="user">'+username+'</li>')
                }
                else {
                    $('#logcheckmsg').html(data)
                }
            }
        })
    });

    $('#upwd').bind('keyup',function (evt) {
        if(evt.keyCode=="13"){
                $.ajax({
                type:'POST',
                url:'/user/login/',
                data:{
                    username : $('#uname').val(),
                    upwd : $('#upwd').val(),
                    issave: $('#issave').prop('checked'),     //用此方法查看是否被选中 而val()取值永远固定
                },
                success: function (data) {
                    if(data=='ok'){
                        $('.container').removeClass('blur');
                        $('.loginbg').fadeOut();
                        $('.login').fadeOut();
                        var username = $('#uname').val();
                        $('.top-links').html('<li id="srcli">\n<input type="text" class="topsrchipt" placeholder="搜索">\n<button class="topsrchbtn"></button>\n</li><a href="javascript:void(0);" id="mylist"><li>我的歌单</li></a>\n<a href="javascript:void(0);" id="logout"><li>退出</li></a>\n<li id="user">'+username+'</li>')
                    }
                    else {
                        $('#logcheckmsg').html(data)
                    }
                }
            })
        }
    });



    $('.top-links').on('click','#mylist',function () {
                i = 'MySongList';
                location.hash = i;
    });


    $('.addlistmenuclose').click(function () {
        $('#addlistmenu').css('visibility','hidden');
    });


    var cancreate = true;
    $('#createlistipt').blur(function () {
        $.ajax({
            type:'GET',
            url:'/createlist/',
            data:{
                songlist_name: $('#createlistipt').val()
            },
            success:function (data) {
                if(data=='该歌单名已经存在'){
                    cancreate = false;
                }
                else{
                    cancreate = true;
                }
                $('#creatlistmsg').html(data)
            }
        })
    });



    $('#createlistsubmit').click(function () {
        if(cancreate){
            $.ajax({
                type:'POST',
                url:'/createlist/',
                data:{
                  songlist_name: $('#createlistipt').val(),
                },
                success:function (data) {
                    $('#createlist').css('visibility','hidden');
                    $('.main').html(data)
                }
            })
        }

    });

    //点击小图标播放
    $('.main').on('click','.plybtn',littlebtn);

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
        $('.plybtn').removeClass('rspbaction');
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
    // 播放列表判断重复与否
    function notexists(lis,li) {
        for(var ii=0;ii<lis.length;ii++){
            if(lis[ii].children[0].children[1].innerHTML == li[0].children[0].children[1].innerHTML){
                return false
            }
        }
        return true
    }

    //结果中点击歌手名 以该名字再次搜索
    $('.main').on('click','.srchsinger',function () {
                i = $(this).html();
                location.hash = i;
    });

    $('.main').on('click','.addlstbtn',function () {
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


/////////////////////////////////////////////////////////////
    //尝试解决前进后退的问题
    var processHash = function () {
        hashStr = location.hash.replace("#", "");
        if (hashStr) hashSearch(hashStr)
    };

    window.onload = processHash;

    window.onhashchange = processHash;


    var hashSearch = function (s) {
        if(!$.trim(s)){
            return;
        }
        else{
            if(s!='MySongList'){
                    $.ajax({
                    url:'/search?s=' + encodeURI(s),
                    type:'get',
                    success:function (resText) {
                        $('.main').html(resText)
                    }
                })
            }
            else{
                $.ajax({
                    type : 'GET',
                    url : '/songlist/',
                    success:function (resText) {
                        $('.main').html(resText);
                    }
                })
            }
        }
    }

























});
