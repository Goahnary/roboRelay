var keyCodes = {};
    keyCodes[119] = "FORWARD";
    keyCodes[97] = "LEFT";
    keyCodes[100] = "RIGHT";
    keyCodes[115] = "BACKWARD";
 
 $(document).keypress(function(e){
 	if(e.which in keyCodes){
 		alert(keyCodes[e.which]);
    }
});