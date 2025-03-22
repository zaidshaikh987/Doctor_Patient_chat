from Bio import Entrez
import google.generativeai as genai
import json

# Configure Google Gemini
genai.configure(api_key="AIzaSyDooyEJKTTh6Dwj7ntEDpBzlf50rzdEk-M")

def load_entities(json_path):
    """Load medical entities from JSON file"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return {
            'symptoms': data.get('symptoms', []),
            'conditions': data.get('conditions', []),
            'medications': data.get('medications', [])
        }
    except Exception as e:
        print(f"Error loading entities: {e}")
        return {'symptoms': [], 'conditions': [], 'medications': []}

def fetch_pubmed_evidence(json_path, max_results=3):
    """Fetch research based on JSON entities"""
    entities = load_entities(json_path)
    
    # Build PubMed query
    search_terms = []
    search_terms += entities['symptoms']
    search_terms += entities['conditions']
    search_terms += [f"{med} therapy" for med in entities['medications']]
    query = " AND ".join(search_terms)

    # PubMed API call
    Entrez.email = "zaidshaikh98848@gmail.com"
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    results = Entrez.read(handle)
    
    # Fetch articles
    articles = []
    for pubmed_id in results["IdList"]:
        with Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml") as handle:
            article = handle.read()
            articles.append(parse_article(article))
    
    return articles

def parse_article(article_xml):
    """Extract article details from bytes XML"""
    xml_str = article_xml.decode('utf-8')
    title = ""
    abstract = ""
    
    if "<ArticleTitle>" in xml_str and "</ArticleTitle>" in xml_str:
        title = xml_str.split("<ArticleTitle>")[1].split("</ArticleTitle>")[0]
    
    if "<AbstractText>" in xml_str and "</AbstractText>" in xml_str:
        abstract = xml_str.split("<AbstractText>")[1].split("</AbstractText>")[0]
    
    return {
        'title': title,
        'abstract': abstract
    }

def summarize_with_gemini(content):
    """Summarize using Google Gemini"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        f"Summarize this medical research in 2 sentences: {content}"
    )
    return response.text

def generate_evidence_report(json_path):
    """Generate evidence report"""
    articles = fetch_pubmed_evidence(json_path)
    
    report = "✅ Evidence Synthesis 📚\n"
    for idx, article in enumerate(articles, 1):
        summary = summarize_with_gemini(f"{article['title']}. {article['abstract']}")
        report += f"\n{idx}. Title: {article['title']}\n   Summary: {summary}\n"
    
    return report

# Example Usage
entities_json = r"C:/Users/MD.ZAID SHAIKH/Documents/AI_Medical_Assistant/backend/models/services/medical_entities.json"
print(generate_evidence_report(entities_json))