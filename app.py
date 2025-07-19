import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import spacy
from textstat import flesch_reading_ease as FRE
import extruct
from w3lib.html import get_base_url

# Function to fetch html with Selenium headless Chrome
def fetch_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        # Wait for page to load. You can add explicit waits if needed.
        html = driver.page_source
    finally:
        driver.quit()
    return html

# Score calculation (same as before)
def compute_scores(html, url):
    soup = bs(html, 'html.parser')
    main = soup.find('main')
    text = main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)

    semantic_tags = ['header', 'main', 'article', 'section', 'footer']
    semantic_score = sum(1 for tag in semantic_tags if soup.find(tag)) / len(semantic_tags)

    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        cleaned_text = ' '.join(sentences)
        readability = FRE(cleaned_text)
    except Exception:
        readability = FRE(text)

    metadata = extruct.extract(html, base_url=url)
    has_jsonld = bool(metadata.get('json-ld'))
    title = soup.find('title')
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    meta_score = int(bool(title) + bool(meta_desc) + bool(og_title)) / 3

    imgs = soup.find_all('img')
    img_alt_score = sum(1 for img in imgs if img.get('alt')) / len(imgs) if imgs else 1

    final_score = (
        semantic_score * 0.25 +
        (readability / 100) * 0.25 +
        int(has_jsonld) * 0.2 +
        meta_score * 0.15 +
        img_alt_score * 0.15
    ) * 100

    return {
        "semantic_score": round(semantic_score, 2),
        "readability_score": round(readability, 2),
        "has_jsonld": has_jsonld,
        "meta_score": round(meta_score, 2),
        "img_alt_score": round(img_alt_score, 2),
        "final_score": round(final_score, 2)
    }

# Streamlit UI
st.title("🔎 AI Web Page Readability & Structure Evaluator")

url = st.text_input("Enter the URL to evaluate:", placeholder="https://example.com")

if st.button("Analyze"):
    if url:
        with st.spinner("Fetching and analyzing..."):
            try:
                html = fetch_html(url)
                scores = compute_scores(html, url)

                st.markdown("### 📊 Scores:")
                st.write(f"**Semantic score:**         {scores['semantic_score']}")
                st.write(f"**Readability score:**      {scores['readability_score']}")
                st.write(f"**Has JSON-LD:**            {scores['has_jsonld']}")
                st.write(f"**Metadata score:**         {scores['meta_score']}")
                st.write(f"**Image alt text score:**   {scores['img_alt_score']}")
                st.markdown(f"### 🧠 Final AI Readability Score: **{scores['final_score']} / 100**")

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid URL.")
