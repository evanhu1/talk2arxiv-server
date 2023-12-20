import scipdf
import requests
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk

nltk.download('punkt')

GROBID_URL = "http://localhost:8070"
CHUNK_MAX_TOKEN_SIZE = 512 * 0.75
paper_metadata = {}

def ping():
    response = requests.get(GROBID_URL + "/api/isalive")
    if response.status_code == 200:
        return True
    else:
        return False

def parse_pdf(url):
    article_dict = scipdf.parse_pdf_to_dict(url, as_list=False, grobid_url=GROBID_URL)
    return article_dict

def create_chunk_text_pairs(pdf_dict):
    chunk_text_pairs = []
    title = pdf_dict['title']
    authors = pdf_dict['authors']
    publication_date = pdf_dict['pub_date']
    abstract = pdf_dict['abstract']
    sections = pdf_dict['sections']

    chunk_text_pairs.append({"embedded_text": "Title", "chunk": title})
    chunk_text_pairs.append({"embedded_text": "Authors", "chunk": authors})
    chunk_text_pairs.append({"embedded_text": "Publication Date", "chunk": publication_date})
    chunk_text_pairs.append({"embedded_text": "Abstract", "chunk": abstract})
    
    for section in sections:
        chunk_text_pairs.append({"embedded_text": f"Section: {section['heading']}", "chunk": section["text"]})
        for chunk in generate_hierarchical_chunks(section["text"]):
            chunk_text_pairs.append({"embedded_text": chunk, "chunk": chunk})
        for chunk in generate_hierarchical_chunks(section["text"], CHUNK_MAX_TOKEN_SIZE // 2):
            chunk_text_pairs.append({"embedded_text": chunk, "chunk": chunk})
    print(chunk_text_pairs)
    return chunk_text_pairs

def generate_hierarchical_chunks(text, chunk_max_token_size=CHUNK_MAX_TOKEN_SIZE):
    sentences = sent_tokenize(text)

    chunk = ""
    chunks = []
    chunk_token_size = 0
    for sentence in sentences:
        sentence_tokens_count = len(word_tokenize(sentence))
        if sentence_tokens_count > chunk_max_token_size:
            chunks.append(sentence)
            continue
        elif chunk_token_size + sentence_tokens_count > chunk_max_token_size:
            chunks.append(chunk)
            chunk = ""
            chunk_token_size = 0
        chunk += " " + sentence
        chunk_token_size += sentence_tokens_count
    if chunk:
        chunks.append(chunk)
    return chunks

def get_metadata(paper_url):
  return "" if paper_url not in paper_metadata else paper_metadata[paper_url]

def split_pdf_into_chunks(url):
  pdf_dict = parse_pdf(url)
  paper_metadata[url] = {"title": pdf_dict['title']}
  return create_chunk_text_pairs(pdf_dict)
