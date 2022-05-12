// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;

// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendMessage();
    }
});

// Read the comment the user is sending to chat and send it to the server over the WebSocket as a JSON string


function Emoji(value) {
    console.log(value);
    const chatBox1 = document.getElementById("who");
    const target = chatBox1.value;
    socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': value, 'target': target, 'Emoji': '1'}));
}

function test() {
    const chatBox1 = document.getElementById("EmojiTable");
    if (chatBox1.hidden){
        chatBox1.hidden = false;
    }
    else{
        chatBox1.hidden = true;
    }
}

function chatRoom() {
    const chatBox1 = document.getElementById("chatRoom");
    if (chatBox1.hidden){
        chatBox1.hidden = false;
    }
    else{
        chatBox1.hidden = true;
    }
}


function sendMessage() {
    const chatBox = document.getElementById("chat-comment");
    const toWho = document.getElementById("who");
    const comment = chatBox.value;
    const target = toWho.value;
    chatBox.value = "";
    chatBox.focus();
    if (comment !== "") {
        try{
            socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': comment, 'target': target, 'Emoji': '0'}));
        }
        catch(e){
			alert("程序报错");
		}
    }
}

// Renders a new chat message to the page
function addMessage(chatMessage) {

    let chat = document.getElementById('chat');
    var Words = document.getElementById("words");
    Words.innerHTML += '<div class="atalk"><span>'+ chatMessage['username'] +' :' + chatMessage["comment"] +'</span></div>';
    document.querySelector(".atalk").scrollIntoView({behavior: "smooth"})
//    alert("New message :)")
    console.log("<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>")

}

// called when the page loads to get the chat_history
function get_chat_history() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessage(message);
            }
        }
    };
    request.open("GET", "/chat-history");
    request.send();
}

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {

    console.log(ws_message)
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'chatMessage':
            addMessage(message);
            break;
        case 'webRTC-offer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
            });
            break;
        case 'webRTC-answer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            break;
        case 'webRTC-candidate':
            alert("start video")
            webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

function startVideo() {
    const constraints = {video: true, audio: true};
    navigator.mediaDevices.getUserMedia(constraints).then((myStream) => {
        const elem = document.getElementById("myVideo");
        elem.srcObject = myStream;

        // Use Google's public STUN server
        const iceConfig = {
            'iceServers': [{'url': 'stun:stun2.1.google.com:19302'}]
        };

        // create a WebRTC connection object
        webRTCConnection = new RTCPeerConnection(iceConfig);

        // add your local stream to the connection
        webRTCConnection.addStream(myStream);

        // when a remote stream is added, display it on the page
        webRTCConnection.onaddstream = function (data) {
            const remoteVideo = document.getElementById('otherVideo');
            remoteVideo.srcObject = data.stream;
        };

        // called when an ice candidate needs to be sent to the peer
        webRTCConnection.onicecandidate = function (data) {
            socket.send(JSON.stringify({'messageType': 'webRTC-candidate', 'candidate': data.candidate}));
        };
    })
}


function connectWebRTC() {
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        webRTCConnection.setLocalDescription(webRTCOffer);
    });

}