// 1. 현재 페이지의 URL 주소에서 파라미터(Query String)를 분석합니다.
const urlParams = new URLSearchParams(window.location.search);

// 2. 원하는 파라미터의 키(Key) 이름으로 값을 가져옵니다.
// 예: 주소창이 ?name=홍길동&gift=커피쿠폰 일 때
const userName = urlParams.get('name'); // "홍길동"
const giftName = urlParams.get('gift'); // "커피쿠폰"

// 3. 값이 존재한다면 화면(HTML)에 안전하게 표시합니다.
if (userName) {
    document.getElementById('user-name').textContent = userName;
}
if (giftName) {
    document.getElementById('gift-name').textContent = giftName;
}