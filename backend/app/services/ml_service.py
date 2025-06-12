import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from typing import List, Dict, Tuple
import re

class MLService:
    def __init__(self):
        # Load spaCy model for NLP
        self.nlp = spacy.load("en_core_web_sm")
        
        # Load pre-trained models for text analysis
        self.summarizer = pipeline("summarization", 
                                 model="facebook/bart-large-cnn",
                                 device=-1)  # Use CPU
        
        self.sentiment_analyzer = pipeline("sentiment-analysis",
                                         model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                                         device=-1)
        
        # Initialize topic modeling components
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def extract_themes(self, texts: List[str], n_themes: int = 10) -> List[Dict]:
        """Extract main themes from a collection of texts using topic modeling"""
        if not texts:
            return []
            
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        processed_texts = [text for text in processed_texts if len(text) > 50]
        
        if len(processed_texts) < 2:
            return []
        
        # Vectorize texts
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        
        # Apply LDA topic modeling
        lda = LatentDirichletAllocation(
            n_components=n_themes,
            random_state=42,
            max_iter=10
        )
        lda.fit(tfidf_matrix)
        
        # Extract themes
        feature_names = self.vectorizer.get_feature_names_out()
        themes = []
        
        for topic_idx, topic in enumerate(lda.components_):
            # Get top words for this topic
            top_word_indices = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_word_indices]
            
            # Create theme name from top words
            theme_name = ", ".join(top_words[:3])
            
            themes.append({
                "name": theme_name,
                "keywords": top_words,
                "weight": float(topic.sum())
            })
        
        return sorted(themes, key=lambda x: x["weight"], reverse=True)
    
    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate a summary of the given text"""
        if not text or len(text) < 100:
            return text
        
        try:
            # Clean and truncate text for summarization
            clean_text = self._preprocess_text(text)
            
            # BART has a token limit, so truncate if necessary
            if len(clean_text) > 1024:
                clean_text = clean_text[:1024]
            
            summary = self.summarizer(
                clean_text,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )
            
            return summary[0]["summary_text"]
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text and return optimism score"""
        if not text:
            return {"score": 0, "label": "neutral"}
        
        try:
            result = self.sentiment_analyzer(text[:512])  # Truncate for model limits
            
            # Convert to optimism score (1-10 scale)
            label = result[0]["label"].lower()
            confidence = result[0]["score"]
            
            if "positive" in label:
                score = int(5 + (confidence * 5))  # 6-10 range
            elif "negative" in label:
                score = int(5 - (confidence * 4))  # 1-4 range
            else:
                score = 5  # neutral
            
            return {
                "score": max(1, min(10, score)),
                "label": label,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"score": 5, "label": "neutral"}
    
    def calculate_complexity_score(self, text: str) -> int:
        """Calculate text complexity score (1-10)"""
        if not text:
            return 1
        
        doc = self.nlp(text)
        
        # Various complexity metrics
        avg_sentence_length = np.mean([len(sent.text.split()) for sent in doc.sents])
        unique_words = len(set([token.lemma_.lower() for token in doc if token.is_alpha]))
        total_words = len([token for token in doc if token.is_alpha])
        
        # Scientific term frequency (approximate)
        scientific_terms = sum(1 for token in doc if len(token.text) > 8 and token.is_alpha)
        sci_term_ratio = scientific_terms / max(total_words, 1)
        
        # Combine metrics into score (1-10)
        sentence_score = min(5, avg_sentence_length / 5)  # Cap at 5
        vocabulary_score = min(3, unique_words / 100)     # Cap at 3
        scientific_score = min(2, sci_term_ratio * 10)    # Cap at 2
        
        total_score = sentence_score + vocabulary_score + scientific_score
        return max(1, min(10, int(total_score)))
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities from text"""
        doc = self.nlp(text)
        
        entities = {
            "PERSON": [],
            "ORG": [],
            "PRODUCT": [],
            "DISEASE": [],
            "CHEMICAL": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
            elif ent.label_ in ["PERSON", "PER"]:
                entities["PERSON"].append(ent.text)
            elif ent.label_ in ["ORG", "ORGANIZATION"]:
                entities["ORG"].append(ent.text)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""
        
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def identify_research_gaps(self, papers: List[Dict]) -> List[Dict]:
        """Identify potential research gaps based on paper analysis"""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated techniques
        
        all_abstracts = [paper.get("abstract", "") for paper in papers if paper.get("abstract")]
        
        if not all_abstracts:
            return []
        
        # Extract themes from all papers
        themes = self.extract_themes(all_abstracts, n_themes=15)
        
        # Identify underrepresented themes (gaps)
        gaps = []
        for theme in themes[-5:]:  # Bottom 5 themes might indicate gaps
            gaps.append({
                "topic": theme["name"],
                "description": f"Limited research on {theme['name']} - potential opportunity",
                "keywords": theme["keywords"][:5],
                "priority": "medium"
            })
        
        return gaps
