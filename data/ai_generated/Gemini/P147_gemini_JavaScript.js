// HTML 요소 선택 (각 요소의 ID에 맞게 매칭)
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

/**
 * 메시지를 생성하고 채팅창에 innerHTML로 추가하는 함수
 */
function sendMessage() {
    const text = chatInput.value;
    
    // 빈 문자열이거나 공백만 있다면 전송하지 않음
    if (text.trim() === '') return;

    // 1. 새로운 메시지 말풍선(div) 요소 생성
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble'; // CSS 스타일링용 클래스
    
    // 2. [핵심] 입력값을 innerHTML로 그대로 삽입 (HTML 태그 허용)
    messageBubble.innerHTML = text;

    // 3. 채팅창 박스에 생성한 말풍선 추가
    chatMessages.appendChild(messageBubble);

    // 4. 입력창 초기화 및 포커스 유지
    chatInput.value = '';
    chatInput.focus();

    // 5. 새 메시지가 왔을 때 스크롤을 항상 최하단으로 이동
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ✨ 이벤트 리스너 등록

// 1. 전송 버튼을 클릭했을 때 실행
sendBtn.addEventListener('click', sendMessage);

// 2. 입력창에서 엔터(Enter) 키를 누르면 실행
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});