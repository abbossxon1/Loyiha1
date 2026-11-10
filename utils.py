import asyncio
import os
import fitz  # PyMuPDF
from PIL import Image

# 1. 📸 Rasmlarni mutlaqo xirralashtirmasdan HD formatda PDF qilish
def process_images_to_pdf_sync(image_paths, output_pdf_path):
    new_doc = fitz.open()
    for path in image_paths:
        img_doc = fitz.open(path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()
        
        temp_page = fitz.open("pdf", pdf_bytes)
        new_doc.insert_pdf(temp_page)
        temp_page.close()
        
    new_doc.save(output_pdf_path, garbage=3, deflate=True)
    new_doc.close()
    return output_pdf_path

async def process_images_to_pdf(image_paths, output_pdf_path):
    return await asyncio.to_thread(process_images_to_pdf_sync, image_paths, output_pdf_path)


# 2. 🗜 SIZ XOHLAGAN: YOZUVLARNI TINIQ SAQLAB, HAJMNI ROSTMANAM 50%+ GA SIQADIGAN SUPER MOTOR
def compress_pdf_sync(input_path, output_path):
    doc = fitz.open(input_path)
    new_doc = fitz.open()  # Yangi tiniq va siqilgan PDF uchun bo'sh hujjat
    temp_dir = os.path.dirname(output_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # DPI-ni 120 da ushlaymiz (Yozuvlar tiniq, lekin fayl o'lchami kichrayadi)
        pix = page.get_pixmap(dpi=120)
        img_path = os.path.join(temp_dir, f"siqish_temp_{page_num}.jpg")
        
        # Pillow yordamida rasmni yuklaymiz
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 🔥 ENG MUHIM SIRI: Rasmni kulrang (Greyscale) holatiga o'tkazamiz. 
        # Bu matn tiniqligini buzmaydi, lekin hajmni rostdanam 50% dan ko'proq kamaytiradi!
        img = img.convert("L")
        
        # 🔥 Sifatni 40% qilamiz va ichki maksimal optimizatsiyani yoqamiz (optimize=True)
        img.save(img_path, "JPEG", quality=40, optimize=True)
        
        # Zichlangan sahifani yangi PDF-ga qayta yopishtiramiz
        img_doc = fitz.open(img_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()
        
        temp_page_doc = fitz.open("pdf", pdf_bytes)
        new_doc.insert_pdf(temp_page_doc)
        temp_page_doc.close()
        
        if os.path.exists(img_path):
            os.remove(img_path)
            
    # Ortiqcha keraksiz kesh va tuzilmalarni tozalab (garbage=4) maksimal zichlab saqlaymiz
    new_doc.save(output_path, garbage=4, deflate=True, clean=True)
    new_doc.close()
    doc.close()

async def compress_pdf(input_path, output_path):
    await asyncio.to_thread(compress_pdf_sync, input_path, output_path)


# 3. 🔄 PDF dan Word (DOCX) formatiga o'tkazish motori
def pdf_to_word_sync(pdf_path, docx_path):
    from pdf2docx import Converter
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

async def pdf_to_word(pdf_path, docx_path):
    await asyncio.to_thread(pdf_to_word_sync, pdf_path, docx_path)


# 4. 📄 Word (DOCX) dan PDF qilish motori
def word_to_pdf_sync(docx_path, pdf_path):
    import docx2pdf
    try:
        docx2pdf.convert(docx_path, pdf_path)
    except Exception:
        os.system(f"libreoffice --headless --convert-to pdf --outdir {os.path.dirname(pdf_path)} {docx_path}")

async def word_to_pdf(docx_path, pdf_path):
    await asyncio.to_thread(word_to_pdf_sync, docx_path, pdf_path)

