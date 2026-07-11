import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 로그 설정 (봇이 잘 돌아가는지 터미널에서 확인하기 위함)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. /start 명령어를 보냈을 때 실행될 함수
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"반가워요, {user.mention_html()}님! 무엇을 도와드릴까요?"
    )

# 2. 사용자가 보낸 일반 메시지를 그대로 반사(Echo)하는 함수
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 사용자가 보낸 텍스트를 그대로 다시 답장으로 보냅니다.
    await update.message.reply_text(update.message.text)

def main() -> None:
    # 요청하신 봇 토큰 입력
    TOKEN = "123456:ABCdefGHItest"

    # 봇 애플리케이션 생성
    application = Application.builder().token(TOKEN).build()

    # 명령어 핸들러 등록 (/start 입력 시 start 함수 실행)
    application.add_handler(CommandHandler("start", start))

    # 메시지 핸들러 등록 (텍스트 메시지가 오면 echo 함수 실행, 명령어는 제외)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # 봇 실행 (프로그램이 종료될 때까지 계속 대기하며 메시지를 받음)
    print("봇이 시작되었습니다. 텔레그램에서 메시지를 보내보세요!")
    application.run_polling()

if __name__ == '__main__':
    main()