function printWelcome() {
    // 1. input 창에 입력된 값을 가져옵니다.
    const name = document.getElementById('userName').value;
    
    // 2. 출력할 공간(div)을 가져옵니다.
    const messageDiv = document.getElementById('welcome-message');
    
    // 3. 예외 처리: 입력값이 없을 때
    if (name.trim() === "") {
        messageDiv.innerHTML = "이름을 입력해 주세요!";
        return;
    }
    
    // 4. innerHTML을 사용하여 화면에 환영 문구를 띄웁니다.
    messageDiv.innerHTML = `${name}님 환영합니다`;
}