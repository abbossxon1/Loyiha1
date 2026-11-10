
import os
import uuid
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

import utils


# =====================================
# SOZLAMALAR
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi! Tokenni sozlang.")

KANAL_ID = -1002488442029
KANAL_LINK = "https://t.me/abbosxon_15"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

session = AiohttpSession(timeout=300)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# =====================================
# HOLATLAR
# =====================================

class BotStates(StatesGroup):
    WAITING_FOR_IMAGES = State()
    WAITING_FOR_COMPRESS = State()
    WAITING_FOR_PDF_TO_WORD = State()
    WAITING_FOR_WORD_TO_PDF = State()


# =====================================
# YORDAMCHI FUNKSIYALAR
# =====================================

def make_path(prefix, extension):
    return str(
        DOWNLOAD_DIR /
        f"{prefix}_{uuid.uuid4().hex}{extension}"
    )


async def download_telegram_file(document, destination):
    await bot.download(
        document,
        destination=destination,
        timeout=180,
        chunk_size=256 * 1024
    )

    if not os.path.isfile(destination):
        raise RuntimeError("Fayl yuklanmadi!")

    if os.path.getsize(destination) == 0:
        raise RuntimeError("Yuklangan fayl bo'sh!")


def remove_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                logger.exception("Faylni o'chirishda xato")


async def delete_message(message):
    try:
        await message.delete()
    except Exception:
        pass


async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(
            chat_id=KANAL_ID,
            user_id=user_id
        )
        return member.status in (
            "creator", "administrator", "member"
        )
    except Exception:
        logger.exception("Obunani tekshirishda xato")
        return False


def subscription_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="📢 Kanalga a'zo bo'lish",
        url=KANAL_LINK
    )
    kb.button(
        text="✅ Tekshirish",
        callback_data="check_subscription"
    )
    kb.adjust(1)
    return kb.as_markup()


def main_keyboard():
    kb = ReplyKeyboardBuilder()

    kb.button(text="📸 Rasmlarni PDF qilish")
    kb.button(text="🗜 PDF hajmini siqish")
    kb.button(text="🔄 PDF -> Word (DOCX)")
    kb.button(text="📄 Word -> PDF qilish")
    kb.button(text="ℹ️ Bot haqida")
    kb.button(text="❓ Yordam")

    kb.adjust(1, 1, 1, 1, 2)

    return kb.as_markup(resize_keyboard=True)


async def require_subscription(message):
    if await check_sub(message.from_user.id):
        return True

    await message.answer(
        "⚠️ Botdan foydalanish uchun kanalga a'zo bo'ling.",
        reply_markup=subscription_keyboard()
    )
    return False


# =====================================
# START
# =====================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):

    await state.clear()

    if not await check_sub(message.from_user.id):
        await message.answer(
            "⚠️ Botdan foydalanish uchun kanalimizga a'zo bo'ling!",
            reply_markup=subscription_keyboard()
        )
        return

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🚀 PDF YORDAMCHI BOTIGA XUSH KELIBSIZ!\n\n"
        "📂 Barcha hujjat xizmatlari bir joyda.\n\n"
        "👇 Kerakli xizmatni tanlang:",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(call: types.CallbackQuery):

    if await check_sub(call.from_user.id):
        await call.answer("A'zolik tasdiqlandi!")
        await delete_message(call.message)

        await call.message.answer(
            "✅ Bot faollashdi!\nKerakli xizmatni tanlang:",
            reply_markup=main_keyboard()
        )
    else:
        await call.answer(
            "Avval kanalga a'zo bo'ling!",
            show_alert=True
        )


# =====================================
# BOT HAQIDA (SUPER DIZAYN VA EMOJILAR)
# =====================================

@dp.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: types.Message):
    if not await check_sub(message.from_user.id): return
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍💻 Dasturchi bilan bog'lanish", url="tg://resolve?domain=rzbyv_1")
    await message.answer(
        "🚀 **Universal Hujjat Yordamchi Bot v2.0**\n\n"
        "📸 *Rasmlarni HD formatda PDF qilish*\n"
        "🗜 *PDF hajmini 50%+ keskin siqish*\n"
        "🔄 *PDF fayllarni Word (DOCX) qilish*\n"
        "📄 *Word hujjatlarini PDF formatiga o'tkazish*\n\n"
        "⚡ **Tezkor, qulay va 100% asinxron yordamchi bot!**\n\n"
        "⚙️ **Tizim qoidalari va limitlari:**\n"
        "• Maksimal fayl yuklash hajmi: **20 MB**\n"
        "• Bitta PDF uchun maksymal rasm: **50 ta**\n\n"
        "🔥 Muammo yoki takliflar bo'lsa, pastdagi tugma orqali dasturchiga to'g'ridan-to'g'ri write qilishingiz mumkin:",
        reply_markup=builder.as_markup()
    )


# -------------------------------------------------------------------------------------



@dp.message(F.text == "❓ Yordam")
async def help_bot(message: types.Message):

    if not await require_subscription(message):
        return

    await message.answer(
        "📚 BOTDAN FOYDALANISH\n\n"
        "1️⃣ Menyudan xizmatni tanlang.\n"
        "2️⃣ Kerakli faylni yuboring.\n"
        "3️⃣ Bot faylni qayta ishlaydi.\n"
        "4️⃣ Tayyor hujjatni qabul qilib oling.\n\n"
        "❗ Muammo bo'lsa faylni qayta yuboring."
    )


# =====================================
# XIZMATLARNI TANLASH: RASMLARNI PDF QILISH
# =====================================

@dp.message(F.text == "📸 Rasmlarni PDF qilish")
async def mode_images(message: types.Message, state: FSMContext):
    if not await check_sub(message.from_user.id):
        return

    await state.set_state(BotStates.WAITING_FOR_IMAGES)
    await state.update_data(images_list=[])

    await message.answer(
        "📸 **PDF qilmoqchi bo'lgan rasmlaringizni ketma-ket yuboring.**\n\n"
        "📥 Maksimal cheklov: **50 tagacha rasm** yuborishingiz mumkin.\n"
        "Tugagach, pastda paydo bo'ladigan '✅ PDF yaratish' tugmasini bosing."
    )

# 📸 RASMLARNI JONLI QABUL QILISH VA 50 TA CHEKLOVINI NAZORAT QILISH
@dp.message(BotStates.WAITING_FOR_IMAGES, F.photo)
async def handle_images(message: types.Message, state: FSMContext):
    data = await state.get_data()
    images_list = data.get("images_list", [])
    
    # 🛑 50 TA RASM CHEKLOVINI TEKSHIRISH
    if len(images_list) >= 50:
        await message.answer(
            "⚠️ **Maksimal cheklovga yetdingiz!**\n\n"
            "Bot bitta PDF faylga maksimal 50 ta rasm qabul qiladi. "
            "Iltimos, pastdagi '✅ PDF yaratish' tugmasini bosing!"
        )
        return

    photo = message.photo[-1]
    file_path = f"downloads/{photo.file_id}.jpg"
    await bot.download(photo, destination=file_path)
    
    images_list.append(file_path)
    await state.update_data(images_list=images_list)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ PDF yaratish", callback_data="generate_pdf")
    
    # Foydalanuvchiga har safar nechanchi rasm muvaffaqiyatli yuklanganini aytib turadi
    await message.answer(
        f"📥 **{len(images_list)}-rasm muvaffaqiyatli yuklandi!**\n"
        f"Yana rasm yuborishingiz mumkin (Maksimal: 50).", 
        reply_markup=builder.as_markup()
    )


# ----- SIZ TASHAGAN KODNING HUJJATBOT.PY O'RTASIGA 100% MOSLASHTIRILGAN VARIANTI -----

@dp.message(F.text == "🗜 PDF hajmini siqish")
async def mode_compress(message: types.Message, state: FSMContext):
    # Kodingizdagi check_sub a'zolik tekshiruv tizimi ulandi
    if not await check_sub(message.from_user.id):
        return

    await state.set_state(BotStates.WAITING_FOR_COMPRESS)

    await message.answer(
        "🗜 **PDF HAJMINI SIQISH (50% ultra-siqish rejimi)**\n\n"
        "📥 Siqmoqchi bo'lgan PDF faylingizni yuboring (Maksimal: 20 MB):"
    )

# -------------------------------------------------------------------------------------


@dp.message(F.text == "🔄 PDF -> Word (DOCX)")
async def mode_pdf_word(message: types.Message, state: FSMContext):

    if not await require_subscription(message):
        return

    await state.set_state(BotStates.WAITING_FOR_PDF_TO_WORD)

    await message.answer(
        "🔄 PDF dan Word formatiga o'tkazish uchun PDF yuboring."
    )


@dp.message(F.text == "📄 Word -> PDF qilish")
async def mode_word_pdf(message: types.Message, state: FSMContext):

    if not await require_subscription(message):
        return

    await state.set_state(BotStates.WAITING_FOR_WORD_TO_PDF)

    await message.answer(
        "📄 PDF qilish uchun DOCX faylingizni yuboring."
    )


# =====================================
# RASMLAR -> PDF
# =====================================

@dp.message(BotStates.WAITING_FOR_IMAGES, F.photo)
async def handle_images(message: types.Message, state: FSMContext):

    path = make_path("image", ".jpg")

    try:
        photo = message.photo[-1]

        await bot.download(
            photo,
            destination=path,
            timeout=180
        )

        data = await state.get_data()
        images = data.get("images_list", [])

        images.append(path)

        await state.update_data(images_list=images)

        kb = InlineKeyboardBuilder()
        kb.button(
            text="✅ PDF yaratish",
            callback_data="generate_pdf"
        )

        await message.answer(
            f"✅ {len(images)} ta rasm qabul qilindi.",
            reply_markup=kb.as_markup()
        )

    except Exception:
        remove_files(path)
        logger.exception("Rasm yuklash xatosi")
        await message.answer("❌ Rasmni yuklashda xato yuz berdi.")


@dp.callback_query(
    BotStates.WAITING_FOR_IMAGES,
    F.data == "generate_pdf"
)
async def generate_pdf(call: types.CallbackQuery, state: FSMContext):

    await call.answer()

    data = await state.get_data()
    images = data.get("images_list", [])

    if not images:
        await call.message.answer("Avval rasm yuboring!")
        return

    output = make_path("result", ".pdf")
    status = await call.message.answer("⏳ PDF tayyorlanmoqda...")

    try:
        await utils.process_images_to_pdf(images, output)

        await call.message.answer_document(
            types.FSInputFile(output),
            caption="✅ PDF muvaffaqiyatli yaratildi!"
        )

    except Exception:
        logger.exception("PDF yaratish xatosi")
        await call.message.answer("❌ PDF yaratishda xatolik yuz berdi.")

    finally:
        await delete_message(status)
        remove_files(*images, output)
        await state.clear()


# =====================================
# PDF SIQISH
# =====================================

@dp.message(
    BotStates.WAITING_FOR_COMPRESS,
    F.document
)
async def handle_compress(message: types.Message, state: FSMContext):

    document = message.document

    if not (document.file_name or "").lower().endswith(".pdf"):
        await message.answer("❌ Faqat PDF fayl yuboring!")
        return

    input_path = make_path("original", ".pdf")
    output_path = make_path("compressed", ".pdf")

    status = await message.answer("📥 PDF yuklanmoqda...")

    try:
        await download_telegram_file(document, input_path)

        await status.edit_text("⚙️ PDF optimallashtirilmoqda...")

        await utils.compress_pdf(input_path, output_path)

        old_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)

        if new_size < old_size:

            percent = (old_size - new_size) / old_size * 100

            await message.answer_document(
                types.FSInputFile(output_path),
                caption=(
                    "✅ PDF optimallashtirildi!\n\n"
                    f"📦 Avval: {old_size / 1048576:.2f} MB\n"
                    f"📉 Keyin: {new_size / 1048576:.2f} MB\n"
                    f"🔥 Kamayish: {percent:.1f}%"
                )
            )

        else:
            await message.answer_document(
                types.FSInputFile(input_path),
                caption=(
                    "ℹ️ PDF allaqachon optimallashtirilgan.\n"
                    "Hajmi kamaymagani uchun asl fayl yuborildi."
                )
            )

        await state.clear()

    except asyncio.TimeoutError:
        logger.exception("Yuklash vaqti tugadi")
        await message.answer(
            "⏱ Yuklash vaqti tugadi. Internetni tekshirib qayta yuboring."
        )

    except Exception:
        logger.exception("PDF siqish xatosi")
        await message.answer(
            "❌ PDF bilan ishlashda xatolik yuz berdi."
        )

    finally:
        await delete_message(status)
        remove_files(input_path, output_path)


# =====================================
# PDF -> WORD
# =====================================

@dp.message(
    BotStates.WAITING_FOR_PDF_TO_WORD,
    F.document
)
async def handle_pdf_to_word(message: types.Message, state: FSMContext):

    document = message.document

    if not (document.file_name or "").lower().endswith(".pdf"):
        await message.answer("❌ PDF fayl yuboring!")
        return

    input_path = make_path("pdf", ".pdf")
    output_path = make_path("word", ".docx")

    status = await message.answer("📥 PDF yuklanmoqda...")

    try:
        await download_telegram_file(document, input_path)

        await status.edit_text("⚙️ Word yaratilmoqda...")

        await utils.pdf_to_word(input_path, output_path)

        await message.answer_document(
            types.FSInputFile(output_path),
            caption="✅ Word hujjatingiz tayyor!"
        )

        await state.clear()

    except asyncio.TimeoutError:
        await message.answer("⏱ Yuklash vaqti tugadi. Qayta urinib ko'ring.")

    except Exception:
        logger.exception("PDF Word xatosi")
        await message.answer("❌ PDF Word formatiga o'tkazilmadi.")

    finally:
        await delete_message(status)
        remove_files(input_path, output_path)


# =====================================
# WORD -> PDF
# =====================================

@dp.message(
    BotStates.WAITING_FOR_WORD_TO_PDF,
    F.document
)
async def handle_word_to_pdf(message: types.Message, state: FSMContext):

    document = message.document

    filename = (document.file_name or "").lower()

    if not filename.endswith((".docx", ".doc")):
        await message.answer("❌ DOC yoki DOCX fayl yuboring!")
        return

    extension = Path(filename).suffix

    input_path = make_path("word", extension)
    output_path = make_path("pdf", ".pdf")

    status = await message.answer("📥 Word yuklanmoqda...")

    try:
        await download_telegram_file(document, input_path)

        await status.edit_text("⚙️ PDF tayyorlanmoqda...")

        await utils.word_to_pdf(input_path, output_path)

        await message.answer_document(
            types.FSInputFile(output_path),
            caption="✅ Word hujjatingiz PDF qilindi!"
        )

        await state.clear()

    except asyncio.TimeoutError:
        await message.answer("⏱ Yuklash vaqti tugadi. Qayta urinib ko'ring.")

    except Exception:
        logger.exception("Word PDF xatosi")
        await message.answer(
            "❌ Word faylni PDF qilishda xatolik yuz berdi."
        )

    finally:
        await delete_message(status)
        remove_files(input_path, output_path)


# =====================================
# BOTNI ISHGA TUSHIRISH
# =====================================

async def main():

    print("Bot muvaffaqiyatli ishga tushdi...")

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
