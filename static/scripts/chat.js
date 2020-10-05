document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    let current;
    console.log(current)

    socket.on('connect', () => {
        console.log("I am connected!")
        console.log(team)
        joinRoom(team)
        current = team;
        document.querySelector('#displaymessage').scrollTop = document.querySelector('#displaymessage').scrollHeight;
        socket.on('system', data => {
            console.log(data["user_id"] + " is " + data["state"])
            if (data["state"] == "active") {
                console.log(document.getElementById(data["user_id"]));
                var ele = document.getElementById(data['user_id']);
                ele.firstElementChild.setAttribute('class', 'active');
                ele.firstElementChild.style.visibility = "";
            }
            else {
                var ele = document.getElementById(data['user_id']);
                ele.firstElementChild.setAttribute('class', 'inactive');
            }
        });
        document.getElementById('file').onchange = () => {
            console.log("Yes");
            var user_message = document.getElementById('user_message');
            user_message.value = file.files[0].name;
        }
        document.querySelector('#sendbutton').onclick = () => {
            console.log("this works")
            var file = document.getElementById('file');
            if (file.files.length) {
                socket.send({ 'type': 2, 'filename': file.files[0].name, 'size': file.files[0].size, 'id': user_id, 'room': team });
                var user_message = document.getElementById('user_message');
                var form = document.getElementById('uploadForm');
                form.submit();
                console.log('form submitted');
                file.value = "";
                user_message.value = "";
            }
            else {
                var text = document.querySelector('#user_message').value;
                if (text != "" && text.trim().length) {
                    socket.send({
                        'type': 1, 'msg': text.trim(),
                        'id': user_id, 'room': team
                    });
                }
            }
        }
        $('#user_message').keypress(function (e) {
            var code = e.keyCode || e.which;
            if (code == 13) {
                text = $('#user_message').val();
                $('#user_message').val('');
                if (text != "" && text.trim().length) {
                    socket.send({
                        'type': 1, 'msg': text.trim(),
                        'id': user_id, 'room': team
                    });
                }
            }
        });

    });

    socket.on('receive', data => {
        console.log("check if prints this works")
        console.log(data.msg + " this is the message")
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const span_message = document.createElement('div');
        span_message.setAttribute("class", "message");
        const br = document.createElement('br');
        if (data.username != name) {
            p.setAttribute("class", "other");
            span_username.setAttribute("class", "othername");
            span_timestamp.setAttribute("class", "time-stamp-left");
            span_username.innerText = data.username;
            if (data.type == 2) {
                console.log("Type is 2")
                var link = document.createElement('a');
                const linkstr = "/download/" + data.room + "/" + data.filename;
                link.setAttribute('href', linkstr);
                console.log(linkstr);
                link.style.wordWrap = "break-word";
                link.innerText = data.filename;
                span_timestamp.innerText = moment(data.time_stamp).calendar();
                p.innerHTML += span_username.outerHTML + br.outerHTML + link.outerHTML + br.outerHTML + span_timestamp.outerHTML
                document.querySelector('#displaymessage').append(p);
            }
            else {
                console.log("Type is 1")
                span_message.innerText = data.msg;
                span_timestamp.innerText = moment(data.time_stamp).calendar();
                p.innerHTML += span_username.outerHTML + br.outerHTML + span_message.outerHTML + br.outerHTML + span_timestamp.outerHTML
                document.querySelector('#displaymessage').append(p);
            }

        } else {
            console.log("okayy")
            p.setAttribute("class", "mymsg");
            span_timestamp.setAttribute("class", "time-stamp-right");
            span_username.innerText = data.username;
            span_username.setAttribute("class", "myname");
            if (data.type == 2) {
                console.log("Type is 2")
                var link = document.createElement('a');
                const linkstr = "/download/" + data.room + "/" + data.filename;
                console.log(linkstr);
                link.setAttribute('href', linkstr);
                link.style.wordWrap = "break-word";
                console.log(linkstr);
                link.innerText = data.filename;
                span_timestamp.innerText = moment(data.time_stamp).calendar();
                p.innerHTML += span_username.outerHTML + br.outerHTML + link.outerHTML + br.outerHTML + span_timestamp.outerHTML
                document.querySelector('#displaymessage').append(p);
            }
            else {
                console.log("Type is 1")
                span_message.innerText = data.msg;
                span_timestamp.innerText = moment(data.time_stamp).calendar();
                p.innerHTML += span_username.outerHTML + br.outerHTML + span_message.outerHTML + br.outerHTML + span_timestamp.outerHTML
                document.querySelector('#displaymessage').append(p);
            }
        }
        document.querySelector('#displaymessage').scrollTop = document.querySelector('#displaymessage').scrollHeight;

    });

    window.onbeforeunload = function () {
        console.log("Yes this works")
        socket.emit('leave', {
            user_id: user_id,
            room: team
        })
        console.log("Let's check")
    };




    function joinRoom(room) {
        console.log("joined")
        socket.emit('join', { 'user_id': user_id, 'room': team });

    }



});
