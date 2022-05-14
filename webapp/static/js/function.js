// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;
let count = 1;

const iceConfig = {
    'iceServers': [{'url': 'stun:stun2.1.google.com:19302'}]
};

// create a WebRTC connection object
webRTCConnection = new RTCPeerConnection(iceConfig);


// called when an ice candidate needs to be sent to the peer
webRTCConnection.onicecandidate = function (data) {
    socket.send(JSON.stringify({'messageType': 'webRTC-candidate', 'candidate': data.candidate}));
};

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
    if (chatBox1.hidden) {
        chatBox1.hidden = false;
    } else {
        chatBox1.hidden = true;
    }
}

function chatRoom() {
    const chatBox1 = document.getElementById("chatRoom");
    if (chatBox1.hidden) {
        chatBox1.hidden = false;
    } else {
        chatBox1.hidden = true;
    }
}

//
// function sendMessage() {
//
//     const chatBox = document.getElementById("chat-comment");
//     const toWho = document.getElementById("who");
//     const comment = chatBox.value;
//     const target = toWho.value;
//     chatBox.value = "";
//     chatBox.focus();
//     if (comment !== "") {
//         try {
//             socket.send(JSON.stringify({
//                 'messageType': 'chatMessage',
//                 'comment': comment,
//                 'target': target,
//                 'Emoji': '0'
//             }));
//             var message = {
//                 "username": "{{username}}",
//                 "comment": comment
//             };
//             addMessage(message)
//
//         } catch (e) {
//             alert("error");
//         }
//     }
// }

// Renders a new chat message to the page
function addMessage(chatMessage) {

    let chat = document.getElementById('chat');
    var Words = document.getElementById("words");
    Words.innerHTML += '<div class="atalk"><span>' + chatMessage['username'] + ' :' + chatMessage["comment"] + '</span></div>';
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
            target = message.target;
            from = message.username;
            addMessage(message);
            if (target != "All users" && target != from) {
                $("#myToast").toast("show");
            }
            break;
        case 'webRTC-offer':
            // alert("offer video");
            startVideo();
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
            });
            break;
        case 'webRTC-answer':
            // alert("answer video")
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));

            break;
        case 'webRTC-candidate':
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

        // add your local stream to the connection
        webRTCConnection.addStream(myStream);

        // when a remote stream is added, display it on the page
        webRTCConnection.onaddstream = function (data) {
            const remoteVideo = document.getElementById('otherVideo');
            remoteVideo.srcObject = data.stream;
        };


    })
}

function sleep(d) {
    for (var t = Date.now(); Date.now() - t <= d;) ;
}


async function offer() {
    var answer = window.confirm("Save data?");
    if (answer) {
        //some code
        await connectWebRTC();
        var answer = window.confirm("Save data?");
        if (answer) {
            //some code
            connectWebRTC()
        } else {
            //some code
        }
    } else {
        //some code
    }



}


function connectWebRTC() {
    // create and send an offer
    startVideo();
    webRTCConnection.createOffer().then(webRTCOffer => {
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        webRTCConnection.setLocalDescription(webRTCOffer);
    });

}