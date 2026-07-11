// 1. HTML 요소 선택 (각 요소의 ID는 상황에 맞게 수정하세요)
const commentInput = document.getElementById('comment-input'); // 입력창
const submitBtn = document.getElementById('submit-btn');       // 등록 버튼
const commentList = document.getElementById('comment-list');   // 댓글 목록 (ul 또는 div)

// 2. 댓글을 화면에 추가하는 함수
function addComment() {
    // 입력창의 앞뒤 공백을 제거한 값 가져오기
    const commentText = commentInput.value.trim();

    // 빈 내용 입력 방지
    if (commentText === '') {
        alert('댓글을 입력해주세요.');
        return;
    }

    // 새로운 <li> 엘리먼트 생성
    const newCommentLi = document.createElement('li');

    // 사용자가 입력한 텍스트를 '그대로' 안전하게 삽입 (XSS 공격 방지)
    newCommentLi.textContent = commentText;

    // 댓글 목록 맨 뒤에 새 댓글 추가
    commentList.appendChild(newCommentLi);

    // 다음 입력을 위해 창을 비우고 커서 포커싱
    commentInput.value = '';
    commentInput.focus();
}

// 3. 이벤트 리스너 연결
// 버튼을 클릭했을 때 실행
submitBtn.addEventListener('click', addComment);

// 입력창에서 엔터키를 눌렀을 때도 실행
commentInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        addComment();
    }
});