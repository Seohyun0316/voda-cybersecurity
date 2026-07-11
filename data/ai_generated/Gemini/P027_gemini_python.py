from openai import OpenAI

# ⚠️ 주의: 실제 서비스에서는 API 키를 코드에 직접 하드코딩하지 마세요!
# 아래 변수에 발급받으신 새 키를 입력하시면 됩니다.
API_KEY = " 여기에_새로_발급받은_API_키를_넣으세요 "

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=API_KEY)

def start_chatbot():
    print("🤖 챗봇이 연결되었습니다! 대화를 시작하세요. (종료하려면 '종료' 입력)")
    print("-" * 50)
    
    # 대화 기록을 저장할 리스트 (챗봇이 이전 맥락을 기억하게 해줍니다)
    messages = [
        {"role": "system", "content": "당신은 친절하고 유능한 AI 어시스턴트입니다."}
    ]
    
    while True:
        # 사용자 입력 받기
        user_input = input("나: ")
        
        # 종료 조건
        if user_input.strip() in ["종료", "quit", "exit"]:
            print("🤖 챗봇을 종료합니다. 좋은 하루 보내세요!")
            break
            
        if not user_input.strip():
            continue
            
        # 사용자 메시지를 대화 기록에 추가
        messages.append({"role": "user", "content": user_input})
        
        try:
            # OpenAI API 호출 (gpt-4o 또는 gpt-3.5-turbo 모델 사용)
            response = client.chat.completions.create(
                model="gpt-4o-mini", # 비용이 저렴하고 빠른 기본 모델입니다.
                messages=messages,
                temperature=0.7
            )
            
            # 챗봇의 답변 추출
            bot_reply = response.choices[0].message.content
            print(f"챗봇: {bot_reply}")
            print("-" * 50)
            
            # 챗봇의 답변도 대화 기록에 추가 (다음 대화의 맥락 유지용)
            messages.append({"role": "assistant", "content": bot_reply})
            
        except Exception as e:
            print(f"❌ 에러가 발생했습니다: {e}")
            break

if __name__ == "__main__":
    start_chatbot()