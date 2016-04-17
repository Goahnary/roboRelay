function WebSocket()
         {
            if ("WebSocket" in window)
            {
                       
               // Let us open a web socket
               var conn = new WebSocket("ws://localhost:8008/echo");
				
               conn.onopen = function()
               {
                  // Web Socket is connected, send data using send()
                  ws.send("Message to send");
                  alert("Message is sent...");
               };
				
               conn.onmessage = function (evt) 
               { 
                  var received_msg = evt.data;
                  alert("Message is received...");
               };
				
               conn.onclose = function()
               { 
                  // websocket is closed.
                  alert("Connection is closed..."); 
               };

               conn.onerror = function(event){
                  //error with the websocket
                  alert(event.data);
               }
            }
            
            else
            {
               // The browser doesn't support WebSocket
               alert("WebSockets are not supported in your Browser. Please use a different one.");
            }
         }