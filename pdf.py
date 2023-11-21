from PyPDF2 import PdfReader
import requests
from io import BytesIO
import scipdf

def read_pdf(url):
    response = requests.get(url)
    return PdfReader(BytesIO(response.content))

def extract_pdf(pdf):
    print("Parsing paper")
    number_of_pages = len(pdf.pages)
    print(f"Total number of pages: {number_of_pages}")
    paper_text = []
    for i in range(number_of_pages):
        page = pdf.pages[i]
        page_text = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            x = tm[4]
            y = tm[5]
            # ignore header/footer
            if (y > 50 and y < 720) and (len(text.strip()) > 1):
                page_text.append({"fontsize": fontSize, "text": text.strip().replace("\x03", ""), "x": x, "y": y})

        _ = page.extract_text(visitor_text=visitor_body)

        blob_font_size = None
        blob_text = ""
        processed_text = []

        print(page_text)

        for t in page_text:
            if t["fontsize"] == blob_font_size:
                blob_text += f" {t['text']}"
                if len(blob_text) >= 200:
                    processed_text.append({"fontsize": blob_font_size, "text": blob_text, "page": i})
                    blob_font_size = None
                    blob_text = ""
            else:
                if blob_font_size is not None and len(blob_text) >= 1:
                    processed_text.append({"fontsize": blob_font_size, "text": blob_text, "page": i})
                blob_font_size = t["fontsize"]
                blob_text = t["text"]
        paper_text += processed_text
    print("Done parsing paper")
    return paper_text

# pdf = read_pdf("https://arxiv.org/pdf/2208.01066.pdf")
# text = extract_pdf(pdf)

url = "https://arxiv.org/pdf/2302.12246.pdf"
article_dict = scipdf.parse_pdf_to_dict(url, as_list=False, grobid_url="https://ox-adjusted-currently.ngrok-free.app")
print(article_dict.keys())
# print(text)