var conn;

function connectWebSocket()
         {
            if ("WebSocket" in window)
            {
                       
               // Let us open a web socket
               conn = new WebSocket("ws://localhost:8008/");
				
               conn.onopen = function()
               {
                  // Web Socket is connected, send data using send()
                  conn.send("Connected");
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
                  alert("Unable to connect to Server. Please Try again");
               }
             }
            
            else
            {
               // The browser doesn't support WebSocket
               alert("WebSockets are not supported in your Browser. Please use a different one.");
            }
            
         }

function sendToServer(msg){
   if(conn != null){
      conn.send(msg);
   }
}