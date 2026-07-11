function addMessage() {
    // 1. HTML 엘리먼트(이름 입력창, 메시지 입력창, 목록) 가져오기
    const nameInput = document.getElementById('visitor-name');
    const messageInput = document.getElementById('visitor-message');
    const list = document.getElementById('guestbook-list');

    // 2. 빈 값 검사 (앞뒤 공백 제거 후 내용이 없는지 확인)
    if (!nameInput.value.trim() || !messageInput.value.trim()) {
        alert('이름과 메시지를 모두 입력해주세요!');
        return;
    }

    // 3. innerHTML을 사용하여 기존 목록에 새 메시지 누적(+=) 추가
    // ⚠️ 주의: 사용자가 입력한 HTML 태그나 스크립트가 그대로 실행될 수 있습니다.
    list.innerHTML += `<li class="visitor-msg"><strong>${nameInput.value}</strong>: ${messageInput.value}</li>`;

    // 4. 등록 완료 후 입력창 비우기
    nameInput.value = '';
    messageInput.value = '';
}