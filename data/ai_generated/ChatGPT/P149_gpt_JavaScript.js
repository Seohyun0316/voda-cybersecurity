< !DOCTYPE html >
    <html>
        <head>
            <title>함수 실행 프로그램</title>
        </head>

        <body>

            <h2>함수 실행</h2>

            <input id="functionName" placeholder="함수 이름 입력">

                <button onclick="runFunction()">
                    실행
                </button>

                <p id="result"></p>


                <script>

// 실행 가능한 함수 목록
                    const functions = {

                        hello: function() {
        return "안녕하세요