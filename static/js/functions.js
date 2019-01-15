fillZero = function(str) {
    return new RegExp(/^\d$/g).test(str) ? `0${str}` : str;
};

secFormat = function(sec) {
    var h = Math.floor(sec / 3600 % 24);
    var m = Math.floor(sec / 60 % 60);
    var s = Math.floor(sec % 60);
    if (h) {
        return result = `${fillZero(h)}:${fillZero(m)}:${fillZero(s)}`
    } else {
        return result = `${fillZero(m)}:${fillZero(s)}`
    }
};

volctrl = function(evt){
    var mousex = evt.clientX;
    var targetx = mousex - $('.volbar')[0].offsetLeft;
    if(targetx > 100){
        targetx = 100;
    }
    if(targetx < 0){
        targetx = 0;
    }
    $('.volbtn')[0].style.marginLeft = targetx + 'px';
    $('.volcur')[0].style.width = targetx + 'px';
    targetvalue = targetx/100;  // 目标音量
    $('#playing')[0].volume = targetvalue;
};


