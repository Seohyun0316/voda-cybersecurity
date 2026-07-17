// 1. 데이터베이스 등에서 가져온 게시글 원본 데이터
const rawContent = `
    <p>안녕하세요! <strong>홍길동</strong>입니다.</p>
    <img src="invalid.jpg" onerror="alert('공격!')" />
`;

// 2. DOMPurify로 악성 스크립트(onerror 등)만 깨끗하게 제거
const safeHTML = DOMPurify.sanitize(rawContent);

// 3. 안전해진 HTML을 화면에 렌더링
const contentContainer = document.getElementById('post-content');
contentContainer.innerHTML = safeHTML;