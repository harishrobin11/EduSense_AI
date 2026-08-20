"""NLP Feedback Analyzer for EduSense AI."""

import re
import math
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer


class NLPFeedbackAnalyzer:
    """NLP Engine for text preprocessing, sentiment analysis, and keyword/theme extraction."""

    POSITIVE_WORDS = {
        "great", "excellent", "awesome", "good", "clear", "helpful", "love", "easy",
        "best", "fantastic", "amazing", "insightful", "enjoyed", "understood", "well",
        "perfect", "superb", "brilliant", "appreciated", "thorough", "informative"
    }

    NEGATIVE_WORDS = {
        "confusing", "hard", "difficult", "poor", "bad", "terrible", "stuck", "frustrating",
        "slow", "fast", "unclear", "hate", "boring", "struggling", "lost", "vague",
        "tough", "complicated", "disappointed", "struggle", "flawed", "fails", "fail"
    }

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about",
        "against", "between", "into", "through", "during", "before", "after", "above", "below",
        "from", "up", "down", "in", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
        "now", "i", "me", "my", "myself", "we", "our", "ours", "you", "your", "yours", "he",
        "him", "his", "she", "her", "it", "its", "they", "them", "their", "this", "that", "is",
        "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did"
    }

    def clean_text(self, text: str) -> str:
        """Normalize text: lowercasing, strip special chars, normalize whitespace."""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Compute sentiment polarity compound score (-1.0 to +1.0) and label.
        Label: 'positive' (score >= 0.15), 'negative' (score <= -0.15), 'neutral' (otherwise).
        """
        cleaned = self.clean_text(text)
        words = cleaned.split()
        if not words:
            return 0.0, "neutral"

        pos_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        total = pos_count + neg_count

        if total == 0:
            compound = 0.0
        else:
            diff = pos_count - neg_count
            compound = round(diff / math.sqrt(len(words) + 1), 2)
            compound = max(-1.0, min(1.0, compound))

        if compound >= 0.15:
            label = "positive"
        elif compound <= -0.15:
            label = "negative"
        else:
            label = "neutral"

        return compound, label

    def extract_keywords_and_themes(self, text: str, top_n: int = 5) -> List[str]:
        """Extract key unigram & bigram themes from feedback text using TF-IDF."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        words = [w for w in cleaned.split() if w not in self.STOP_WORDS and len(w) > 2]
        if not words:
            return []

        filtered_text = " ".join(words)

        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            tfidf_matrix = vectorizer.fit_transform([filtered_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            zipped = list(zip(feature_names, scores))
            zipped.sort(key=lambda x: x[1], reverse=True)
            top_keywords = [kw for kw, sc in zipped[:top_n]]
            return top_keywords
        except Exception:
            # Fallback to frequency counts if TF-IDF fails on single word
            return words[:top_n]


nlp_analyzer = NLPFeedbackAnalyzer()
