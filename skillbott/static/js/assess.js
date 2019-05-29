function clearQuestIcon(topic) {
    document.getElementById(String(topic)+'_questicon').style.backgroundImage = 'none';
}

function resetYellow(topic) {
    document.getElementById(String(topic)+'_yellowbtn1').checked = false;
    document.getElementById(String(topic)+'_yellowbtn2').checked = false;
    document.getElementById(String(topic)+'_yellowbtn3').checked = false;
}

function resetGreen(topic) {
    document.getElementById(String(topic)+'_greenbtn1').checked = false;
    document.getElementById(String(topic)+'_greenbtn2').checked = false;
    document.getElementById(String(topic)+'_greenbtn3').checked = false;
}

function borderGreen(border, topic) {
    if (document.readyState != 'complete')
        return;
    if (border == true) {
        // do not create border if there is already a green button checked
        if (document.getElementById(String(topic)+'_greentd1').style.borderStyle == 'none') {
            var btn1_checked = document.getElementById(String(topic)+'_greenbtn1').checked;
            var btn2_checked = document.getElementById(String(topic)+'_greenbtn2').checked;
            var btn3_checked = document.getElementById(String(topic)+'_greenbtn3').checked;
            if (btn1_checked || btn2_checked || btn3_checked) {
                return;
            }
        }
    }
    if (border == true) {
        document.getElementById(String(topic)+'_greentd1').style.borderLeft='3px solid red';
        document.getElementById(String(topic)+'_greentd1').style.borderTop='3px solid red';
        document.getElementById(String(topic)+'_greentd1').style.borderBottom='3px solid red';
        document.getElementById(String(topic)+'_greentd2').style.borderTop='3px solid red';
        document.getElementById(String(topic)+'_greentd2').style.borderBottom='3px solid red';
        document.getElementById(String(topic)+'_greentd3').style.borderRight='3px solid red';
        document.getElementById(String(topic)+'_greentd3').style.borderTop='3px solid red';
        document.getElementById(String(topic)+'_greentd3').style.borderBottom='3px solid red';
    }
    else {
        document.getElementById(String(topic)+'_greentd1').style.borderStyle='none';
        document.getElementById(String(topic)+'_greentd2').style.borderStyle='none';
        document.getElementById(String(topic)+'_greentd3').style.borderStyle='none';
        clearQuestIcon(topic);
    }
}

function disableYellow(setting, reset, topic) {
    document.getElementById(String(topic)+'_yellowbtn1').disabled=setting;
    document.getElementById(String(topic)+'_yellowbtn2').disabled=setting;
    document.getElementById(String(topic)+'_yellowbtn3').disabled=setting;
    if (reset == true) {
        resetYellow(topic);
    }
}

function disableGreen(setting, reset, topic) {
    document.getElementById(String(topic)+'_greenbtn1').disabled=setting;
    document.getElementById(String(topic)+'_greenbtn2').disabled=setting;
    document.getElementById(String(topic)+'_greenbtn3').disabled=setting;
    borderGreen(!setting, topic);
    if (reset == true) {
        resetGreen(topic);
        disableOther(setting, topic);
    }
}

function disableOther(setting, topic) {
    document.getElementById(String(topic)+'_other').disabled=setting;
}

