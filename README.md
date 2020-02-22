# wss
Simple [websocket](https://en.wikipedia.org/wiki/WebSocket) (wss or ws) server.

## About
This server was written by me for realize simple flow: 
1. Client open website and want to get some special file (archieve)
2. Client enters his name, email and some poll answers.
3. We generate 6-digit code and send verifications letter on client's email.
4. Client opens letter and fill "code" field
5. If code was right - client may download file by temporary-link
6. Client banned by email and can't download file twice

```


                                    +-----------------+
                                    | webserver.py    |
          +-------------------------+                 +-----------------------------+
          |                         +--------+--------+                             |
          |                                  |                                      |
          |                                  |                                      |
          |                                  |                                      |
 +--------+--------+                +--------+--------+                +------------+---------+
 |   mailagent.py  |                | databaseagent.py|                | digitaloceanagent.py |
 |                 |                |                 |                |                      |
 +-----------------+                +-----------------+                +----------------------+
          +                                  +                                          +
          |                                  |                                          |
          v                                  v                                          v
 +-----------------+                    --------                                  +-----------------+
 |  smtp.gmail.com |                  +-        -+                                |  Digital Ocean  |
 |                 |                  |          |                                |                 |
 +-----------------+                  |          |                                +-----------------+
          +                           |          |                                           +
          |                           | MongoDB  |                                           |
          v                           |          |                                           v
      +-------+                       |          |                                       +------+
      |       |                       |          |                                       |      |
      | CODE  |                       +-        -+                                       | FILE |
      |       |                         --------                                         |      |
      +-------+                                                                          +------+
      
```
## Preparing
•Be sure mongod is running
```
systemctl start mongo
```
•Install all dependencies
```
python3 -m pip install -r requirements.txt
```
•Enable insecure connections in settings of your email provider
•Create API key in digital ocean or whatever you use...

## How to run it

Firstly you need to define some envs (because of to store passwords in repositories is veeeeery bad idea)

SMTP_LOGIN - Your email login  
SMTP_PASS - Your email password   
DIGOC_KEY - Digital Ocean key  
DIGOC_SECRET - Digital Ocean secret  
  
Secondly you need to define paths to the ssl-sertificates in *config.py*  
```
SSL = {
    "cert": r"/etc/letsencrypt/live/mysite.com/fullchain.pem",
    "key": r"/etc/letsencrypt/live/mysite.com/privkey.pem"
}
```
In config you can see map hash->realfilename
The client shouldn't be given the opportunity to steal all your files by brute force
```
FILES_MAP = {  # real filenames disguised by hashes
    "c05fbf4fea5db3648bc1634acc3668bd": "funny_dog.mkv"
}
```
# How to use it from another side

```
var socket = new WebSocket("ws://127.0.0.1:1337");

socket.onerror = reconnect;
function reconnect(){
	socket = new WebSocket("ws://127.0.0.1:1337");
	socket.onerror = reconnect;
};

socket.onopen = function(e){
	console.log("Connected to ws://127.0.0.1:1337");
};

socket.onmessage = function(e){
	data = JSON.parse(e.data);
	if (data["response"] == "registered"){
          ...
  }
```
Recieved!

And send back...

```
let request = {
			  "type": "register",
			  "content": "file",
			  "sign": "c05fbf4fea5db3648bc1634acc3668bd",
			  "metadata": ""
			};
ready_request = JSON.stringify(request);
socket.send(ready_request);
```
