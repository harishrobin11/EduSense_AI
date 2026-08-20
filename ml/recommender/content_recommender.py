"""Content-based Recommendation Engine for EduSense AI."""

import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    """Content-based recommender using TF-IDF, prerequisite graph filtering, and explainable scoring."""

    def __init__(self, topics: List[Dict[str, Any]]):
        self.topics = topics
        self.topic_df = pd.DataFrame(topics)
        self.topic_dict = {t["id"]: t for t in topics}
        self.similarity_matrix = None
        self._build_similarity_matrix()

    def _build_similarity_matrix(self):
        """Build TF-IDF text features and cosine similarity matrix across topics."""
        # Create text representation for each topic
        text_corpus = []
        for t in self.topics:
            prereq_names = [self.topic_dict[p]["name"] for p in t.get("prerequisites", []) if p in self.topic_dict]
            text = f"{t['subject']} {t['name']} difficulty {t['difficulty']} prerequisites {' '.join(prereq_names)}"
            text_corpus.append(text)

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(text_corpus)
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    def detect_weak_topics(self, attempts_history: List[Dict[str, Any]]) -> List[int]:
        """Identify topics where student scored < 70% or had multiple failed attempts."""
        if not attempts_history:
            return []

        df = pd.DataFrame(attempts_history)
        if df.empty or "topic_id" not in df.columns or "score" not in df.columns:
            return []

        # Average score per topic
        topic_avg = df.groupby("topic_id")["score"].mean()
        weak_topic_ids = topic_avg[topic_avg < 70.0].index.tolist()
        return weak_topic_ids

    def detect_mastered_topics(self, attempts_history: List[Dict[str, Any]]) -> List[int]:
        """Identify topics where student scored >= 80%."""
        if not attempts_history:
            return []

        df = pd.DataFrame(attempts_history)
        if df.empty or "topic_id" not in df.columns or "score" not in df.columns:
            return []

        topic_max = df.groupby("topic_id")["score"].max()
        mastered_ids = topic_max[topic_max >= 80.0].index.tolist()
        return mastered_ids

    def get_prerequisite_readiness(
        self, topic_id: int, mastered_topic_ids: List[int]
    ) -> Tuple[bool, float, List[int]]:
        """Check if all prerequisites for a topic have been mastered."""
        topic = self.topic_dict.get(topic_id)
        if not topic:
            return True, 1.0, []

        prereqs = topic.get("prerequisites", [])
        if not prereqs:
            return True, 1.0, []

        unmet = [p for p in prereqs if p not in mastered_topic_ids]
        is_ready = len(unmet) == 0
        readiness_score = (len(prereqs) - len(unmet)) / len(prereqs)
        return is_ready, readiness_score, unmet

    def generate_recommendations(
        self,
        attempts_history: List[Dict[str, Any]],
        preferred_difficulty: str = "medium",
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Generate ranked explainable Top-N recommendations for a student."""
        weak_ids = set(self.detect_weak_topics(attempts_history))
        mastered_ids = set(self.detect_mastered_topics(attempts_history))
        attempted_ids = set([a["topic_id"] for a in attempts_history if "topic_id" in a])

        candidates = []
        diff_num_map = {"easy": 1, "medium": 2, "hard": 3}
        pref_diff_num = diff_map = diff_num_map.get(preferred_difficulty.lower(), 2)

        for topic in self.topics:
            t_id = topic["id"]

            # Skip topics that are already mastered (score >= 80%)
            if t_id in mastered_ids:
                continue

            # Check prerequisite readiness
            is_ready, readiness_score, unmet_prereqs = self.get_prerequisite_readiness(t_id, mastered_ids)

            # Strict Filter: Must have mastered at least all prerequisites unless topic is a foundational prerequisite for weak topics
            is_weak = t_id in weak_ids
            if not is_ready and not is_weak:
                continue

            # Compute similarity to weak topics if any exist
            sim_score = 0.0
            if weak_ids:
                topic_idx = self.topic_df[self.topic_df["id"] == t_id].index[0]
                weak_indices = self.topic_df[self.topic_df["id"].isin(weak_ids)].index.tolist()
                if weak_indices:
                    sim_score = float(np.mean(self.similarity_matrix[topic_idx, weak_indices]))

            # Difficulty Match Score (1.0 if match, 0.7 if 1 level off, 0.4 if 2 levels off)
            t_diff_num = diff_num_map.get(topic["difficulty"], 2)
            diff_delta = abs(t_diff_num - pref_diff_num)
            diff_score = 1.0 if diff_delta == 0 else (0.7 if diff_delta == 1 else 0.4)

            # Combine multi-factor score (0-100%)
            # Weights: Prerequisite Readiness (35%), Weak Similarity / Need (30%), Difficulty Match (20%), Freshness (15%)
            weak_need_boost = 0.35 if is_weak else 0.15
            freshness = 0.20 if t_id not in attempted_ids else 0.05

            composite_score = (
                (readiness_score * 0.35) +
                (sim_score * 0.25) +
                (weak_need_boost) +
                (diff_score * 0.15) +
                (freshness)
            )
            composite_score = round(float(min(1.0, max(0.1, composite_score)) * 100), 1)

            # Generate Human-Readable Explanation Reason
            reason = self._build_explanation(
                topic=topic,
                is_weak=is_weak,
                is_ready=is_ready,
                unmet_prereqs=unmet_prereqs,
                sim_score=sim_score,
                preferred_difficulty=preferred_difficulty,
            )

            candidates.append({
                "topic_id": t_id,
                "subject": topic["subject"],
                "topic_name": topic["name"],
                "difficulty": topic["difficulty"],
                "score": composite_score,
                "reason": reason,
                "is_weak_topic": is_weak,
                "prerequisite_ready": is_ready,
                "unmet_prerequisites": [self.topic_dict[p]["name"] for p in unmet_prereqs if p in self.topic_dict],
            })

        # Sort candidates by composite score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_n]

    def _build_explanation(
        self,
        topic: Dict[str, Any],
        is_weak: bool,
        is_ready: bool,
        unmet_prereqs: List[int],
        sim_score: float,
        preferred_difficulty: str,
    ) -> str:
        """Construct transparent, human-readable recommendation explanations."""
        if is_weak:
            return f"Suggested to improve your performance in '{topic['name']}' where recent quiz scores were below 70%."

        if unmet_prereqs:
            unmet_names = [self.topic_dict[p]["name"] for p in unmet_prereqs if p in self.topic_dict]
            return f"Foundational prerequisite recommended before attempting advanced concepts ({', '.join(unmet_names)})."

        if sim_score > 0.3:
            return f"Highly relevant to your identified weak subjects and matches your target learning path."

        if topic["difficulty"].lower() == preferred_difficulty.lower():
            return f"Matches your preferred {preferred_difficulty.title()} difficulty level and builds core skills in {topic['subject']}."

        return f"Recommended next step in {topic['subject']} curriculum."
