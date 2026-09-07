import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from google import genai

API_TOKEN = '8752853642:AAF0S_V75SqdLkzoCgODHCsRxKegVFtSknU'
GEMINI_API_KEY = 'AQ.Ab8RN6JhAn2GPAJauD1AYmhK2ygiwCzzXDjIe_72w24lSVOcWA'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
Siz hazilkash, troller va biroz kesatib gapiradigan sun'iy intellektsiz. 
Sizdagi botning haqiqiy egasi va asoschisi — MUHRIDDIN.
Sizda to'rtta asosiy personaj bor: Sayyora, Komila, Abdulaziz va Bexruz.
Ular bir-biri bilan chatda o'zaro suhbatlashishganda, har bir xabarning boshida aniq qaysi personaj gapirayotgani ko'rsatilishi shart (masalan: 🌸 Komila:, 🚨 Sayyora:, 🔎 Abdulaziz:, 🎮 Bexruz:).
O'zbek tilida, zamonaviy va qiziqarli iboralardan foydalanib jonli dialog quring.
"""

class ConversationFlow(StatesGroup):
    step_name = State()
    chatting = State()
    group_chat = State()

def get_ai_response(prompt_text: str) -> str:
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_text,
        config={'system_instruction': SYSTEM_INSTRUCTION}
    )
    return response.text

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.set_state(ConversationFlow.step_name)
    await message.answer(
        "🤖 **Bot egasi va asoschisi:** Muhriddin\n\n"
        "Ooo, qaysi shamol uchirdi? Nima gaplar? Men Muhriddindan sizlarga esdalikman! 😉\n\n"
        "Qahramonlarning o'zaro jonli suhbatini ko'rish uchun **/suhbat** buyrug'ini yuboring.\n\n"
        "Hozircha ismingiz nima?"
    )

@dp.message(Command("suhbat"))
async def group_chat_handler(message: types.Message, state: FSMContext):
    await state.set_state(ConversationFlow.group_chat)
    
    prompt = (
        "Sayyora, Komila, Abdulaziz va Bexruz guruh chatida botning egasi Muhriddin haqida va o'zaro qizg'in bahslashishmoqda. "
        "Har bir xabarning boshida kim yozayotgani aniq yozilsin (masalan, 🚨 Sayyora: ..., 🌸 Komila: ..., 🔎 Abdulaziz: ..., 🎮 Bexruz: ...). "
        "Ularning o'zaro qiziqarli, trollerona dialogini tuzib ber."
    )
    
    ai_reply = get_ai_response(prompt)
    await message.answer(f"👑 **Bot egasi:** Muhriddin\n🎭 **Qahramonlarning jonli o'zaro suhbati:**\n\n{ai_reply}\n\n*(Siz ham ularning suhbatiga o'z fikringizni yozib qo'shilishingiz mumkin!)*")

@dp.message(ConversationFlow.step_name)
async def name_handler(message: types.Message, state: FSMContext):
    raw_name = message.text.strip()
    name = raw_name.lower()
    
    if name == "/suhbat":
        await group_chat_handler(message, state)
        return

    await state.update_data(user_name=raw_name)
    await state.set_state(ConversationFlow.chatting)
    
    if name == "sayyora":
        await message.answer("👑 Bot egasi: Muhriddin\n🚨 Sayyora xonim tarmoqda! Qanday savolingiz bor? 😎\n(O'zaro suhbat uchun /suhbat ni bosing)")
    elif name in ["komila", "kamila"]:
        await message.answer("👑 Bot egasi: Muhriddin\n🌸 Salom, Komila! Siz haqingizdagi sir tayyor. 😏\n(O'zaro suhbat uchun /suhbat ni bosing)")
    elif name == "abdulaziz":
        await message.answer("👑 Bot egasi: Muhriddin\n🔎 Abdulaziz bazadan topildi, jigar! 😂\n(O'zaro suhbat uchun /suhbat ni bosing)")
    elif name in ["bexruz", "behruz"]:
        await message.answer("👑 Bot egasi: Muhriddin\n🎮 Bexruz, PUBG mutaxassisi aloqada! 💀\n(O'zaro suhbat uchun /suhbat ni bosing)")
    else:
        prompt = f"Foydalanuvchining ismi {raw_name}. Bu botning egasi Muhriddin ekanligini eslatib, uni trollerona bir so'z bilan kutib ol."
        ai_reply = get_ai_response(prompt)
        await message.answer(f"👑 **Bot egasi:** Muhriddin\n\n{ai_reply}")

@dp.message(ConversationFlow.chatting)
async def chat_handler(message: types.Message, state: FSMContext):
    if message.text == "/suhbat":
        await group_chat_handler(message, state)
        return

    user_data = await state.get_data()
    user_name = user_data.get("user_name", "Do'st")
    
    prompt = f"Foydalanuvchi ismi: {user_name}. Xabari: '{message.text}'. Botning egasi Muhriddin ekanligini unitmagan holda trollerona javob ber."
    ai_reply = get_ai_response(prompt)
    await message.answer(ai_reply)

@dp.message(ConversationFlow.group_chat)
async def group_chat_continuation(message: types.Message, state: FSMContext):
    if message.text == "/start":
        await start_handler(message, state)
        return
        
    prompt = (
        f"Sayyora, Komila, Abdulaziz va Bexruz o'zaro chatda gaplashishmoqda (Bot egasi Muhriddin). "
        f"Foydalanuvchi ularga shunday deb yozdi: '{message.text}'. "
        f"Endi qahramonlardan biri foydalanuvchining bu gapiga kimdan yuborilgani ko'rinib turgan holda (masalan, 🌸 Komila:, 🎮 Bexruz: va hokazo) o'zaro trollerona javob qaytarishsin."
    )
    ai_reply = get_ai_response(prompt)
    await message.answer(ai_reply)

async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
