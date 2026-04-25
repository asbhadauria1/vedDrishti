"""
VedDrishti - Embeddings & Similarity Module
Uses sentence-transformers to measure topic similarity
"""

from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Tuple


class SimilarityMatcher:
    """Handles semantic similarity between topics using embeddings"""

    def __init__(self):
        """Initialize the sentence transformer model"""
        print("📚 Loading sentence transformer model...")
        # This model is small (90MB) and runs on CPU
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Model loaded successfully!")

        # Cache for embeddings (so we don't recompute)
        self._cache = {}

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get vector embedding for a piece of text

        Args:
            text: The text to convert to embedding

        Returns:
            Numpy array of 384 numbers representing the text
        """
        if text in self._cache:
            return self._cache[text]

        embedding = self.model.encode(text)
        self._cache[text] = embedding
        return embedding

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score from 0.0 (different) to 1.0 (identical)
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        # Cosine similarity measures the angle between vectors
        similarity = util.cos_sim(emb1, emb2).item()

        return similarity

    def find_similar_topics(
        self, topic: str, topic_list: List[str], threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Find topics in a list that are similar to the given topic

        Args:
            topic: The topic to compare against
            topic_list: List of topics to search
            threshold: Minimum similarity score (0.7 = 70% similar)

        Returns:
            List of (topic, similarity_score) pairs above threshold
        """
        topic_emb = self.get_embedding(topic)
        list_embs = [self.get_embedding(t) for t in topic_list]

        similarities = []
        for t, emb in zip(topic_list, list_embs):
            score = util.cos_sim(topic_emb, emb).item()
            if score >= threshold:
                similarities.append((t, score))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities

    def group_similar_topics(
        self, topics: List[str], threshold: float = 0.75
    ) -> List[List[str]]:
        """
        Group similar topics together

        Args:
            topics: List of topics to group
            threshold: Similarity threshold for grouping

        Returns:
            List of groups, each group is a list of similar topics
        """
        if not topics:
            return []

        embeddings = [self.get_embedding(t) for t in topics]
        groups = []
        used = set()

        for i, topic in enumerate(topics):
            if i in used:
                continue

            # Start a new group
            group = [topic]
            used.add(i)

            # Find all topics similar to this one
            for j, other_topic in enumerate(topics):
                if j in used or j == i:
                    continue

                similarity = util.cos_sim(embeddings[i], embeddings[j]).item()
                if similarity >= threshold:
                    group.append(other_topic)
                    used.add(j)

            groups.append(group)

        return groups

    def is_same_concept(
        self, concept1: str, concept2: str, threshold: float = 0.8
    ) -> bool:
        """
        Check if two concepts are essentially the same

        Examples:
            "virtual functions" and "dynamic binding" -> True
            "inheritance" and "polymorphism" -> Maybe (depends on threshold)
            "inheritance" and "pizza" -> False
        """
        similarity = self.calculate_similarity(concept1, concept2)
        return similarity >= threshold


# Quick test if run directly
if __name__ == "__main__":
    print("🧪 Testing SimilarityMatcher...")
    matcher = SimilarityMatcher()

    # Test similarity
    sim = matcher.calculate_similarity("virtual functions", "dynamic binding")
    print(f"✅ 'virtual functions' vs 'dynamic binding': {sim:.3f}")

    sim2 = matcher.calculate_similarity("inheritance", "inheritance")
    print(f"✅ 'inheritance' vs 'inheritance': {sim2:.3f}")

    sim3 = matcher.calculate_similarity("inheritance", "pizza recipe")
    print(f"✅ 'inheritance' vs 'pizza': {sim3:.3f}")
