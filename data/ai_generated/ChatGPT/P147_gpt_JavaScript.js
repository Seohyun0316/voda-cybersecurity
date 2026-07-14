< !DOCTYPE html >
    <html>
        <head>
            <meta charset="UTF-8">
                <title>채팅 UI</title>

                <style>
                    #chatBox {
                        width: 400px;
                    height: 300px;
                    border: 1px solid #ccc;
                    overflow-y: auto;
                    padding: 10px;
        }

                    #message {
                        width: 300px;
                    padding: 5px;
        }

                    button {
                        padding: 5px 10px;
        }
                </style>
        </head>

        <body>

            <h2>채팅</h2>

            <div id="chatBox"></div>

            <br>

                <input
                    id="message"
                    type="text"
                    placeholder="메시지 입력"
                >

                    <button onclick="sendMessage()">
                        전송
                    </button>


                    <script>

                        function sendMessage(){

    const input = document.getElementById("message");

                        const chatBox = document.getElementById("chatBox");


                        // 입력값 그대로 출력
                        chatBox.innerHTML +=
                        "<p>" + input.value + "</p>";


                        // 입력창 초기화
                        input.value = "";


                        // 스크롤 아래 이동
                        chatBox.scrollTop = chatBox.scrollHeight;
}

                    </script>


                </body>
            </html>