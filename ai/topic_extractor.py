"""
VedDrishti - Topic Extractor Module
Extracts and ranks topics from past papers and transcripts using AI
"""

import re
from collections import Counter
from typing import List, Dict, Set, Tuple

# Handle both direct execution and module import
try:
    from .ollama_client import OllamaClient
    from .embeddings import SimilarityMatcher
except ImportError:
    # When running directly, use absolute imports
    from ollama_client import OllamaClient
    from embeddings import SimilarityMatcher


class TopicExtractor:
    """Extracts topics from course materials using AI and NLP"""

    def __init__(self):
        """Initialize the topic extractor"""
        print("🔧 Initializing Topic Extractor...")
        self.ai_client = OllamaClient()
        self.similarity = SimilarityMatcher()

        # Common COMP2012 topics (for fallback/validation)
        self.common_topics = [
            "inheritance",
            "polymorphism",
            "encapsulation",
            "abstraction",
            "classes",
            "objects",
            "constructors",
            "destructors",
            "virtual functions",
            "dynamic binding",
            "static binding",
            "templates",
            "exception handling",
            "STL",
            "containers",
            "pointers",
            "references",
            "memory management",
            "operator overloading",
            "friend functions",
            "multiple inheritance",
            "abstract classes",
            "interfaces",
            "design patterns",
            "UML",
            "composition",
            "aggregation",
        ]

    def extract_from_past_paper(self, text: str, paper_year: int = None) -> List[Dict]:
        """
        Extract topics from a past exam paper

        Args:
            text: The extracted text from the PDF
            paper_year: Year of the paper (for weighting)

        Returns:
            List of topics with frequency and importance
        """
        print(
            f"📄 Analyzing past paper{' from ' + str(paper_year) if paper_year else ''}..."
        )

        # Method 1: AI extraction
        ai_topics = self.ai_client.extract_topics(text, source_type="paper")

        # Method 2: Keyword extraction (fallback)
        keyword_topics = self._extract_keywords(text)

        # Combine both methods
        all_topics = self._combine_topic_lists(ai_topics, keyword_topics)

        # Calculate frequencies
        topic_frequencies = self._calculate_frequencies(text, all_topics)

        # Build result
        results = []
        for topic in all_topics:
            freq = topic_frequencies.get(topic, 1)
            results.append(
                {
                    "topic": topic,
                    "frequency": freq,
                    "source": "past_paper",
                    "paper_year": paper_year,
                    "raw_importance": min(1.0, freq / 10),  # Normalize frequency to 0-1
                }
            )

        # Sort by frequency
        results.sort(key=lambda x: x["frequency"], reverse=True)

        print(f"   ✅ Extracted {len(results)} topics")
        return results

    def extract_from_transcript(self, text: str, lecture_num: int = None) -> List[Dict]:
        """
        Extract topics from a lecture transcript with emphasis detection

        Args:
            text: The transcript text
            lecture_num: Lecture number (for reference)

        Returns:
            List of topics with emphasis scores
        """
        print(
            f"📝 Analyzing transcript{' (Lecture ' + str(lecture_num) + ')' if lecture_num else ''}..."
        )

        # Get AI-detected emphasis
        emphasized_topics = self.ai_client.detect_emphasis(text)

        # Extract all topics using keyword method
        keyword_topics = self._extract_keywords(text)

        # Calculate mention frequency
        topic_counts = {}
        for topic in keyword_topics:
            # Count how many times the topic appears
            count = len(
                re.findall(r"\b" + re.escape(topic) + r"\b", text, re.IGNORECASE)
            )
            topic_counts[topic] = count

        # Build results with emphasis scores
        results = []

        # First, add AI-detected emphasized topics
        for item in emphasized_topics:
            topic = item.get("topic", "")
            if topic:
                results.append(
                    {
                        "topic": topic.lower(),
                        "mention_count": topic_counts.get(topic.lower(), 1),
                        "emphasis_score": item.get("emphasis_score", 0.5),
                        "context": item.get("context", ""),
                        "source": "transcript_ai",
                    }
                )

        # Then add other topics that appear frequently
        for topic, count in topic_counts.items():
            # Skip if already added
            if not any(r["topic"] == topic for r in results):
                if count >= 2:  # Only include topics mentioned at least twice
                    results.append(
                        {
                            "topic": topic,
                            "mention_count": count,
                            "emphasis_score": min(1.0, count / 10),  # Normalize
                            "context": "",
                            "source": "transcript_frequency",
                        }
                    )

        # Sort by emphasis score
        results.sort(key=lambda x: x["emphasis_score"], reverse=True)

        print(f"   ✅ Extracted {len(results)} topics with emphasis scores")
        return results

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords using simple NLP (fallback method)

        Args:
            text: The text to analyze

        Returns:
            List of keywords
        """
        # Convert to lowercase
        text_lower = text.lower()

        # Find all words that match common COMP2012 topics
        found_topics = []
        for topic in self.common_topics:
            # Look for exact word boundaries
            pattern = r"\b" + re.escape(topic) + r"\b"
            if re.search(pattern, text_lower):
                found_topics.append(topic)

            # Also look for plural forms
            pattern_plural = r"\b" + re.escape(topic) + r"s\b"
            if re.search(pattern_plural, text_lower) and topic not in found_topics:
                found_topics.append(topic)

        return list(set(found_topics))  # Remove duplicates

    def _combine_topic_lists(
        self, ai_topics: List[str], keyword_topics: List[str]
    ) -> List[str]:
        """
        Combine AI-extracted and keyword-extracted topics using similarity matching

        Args:
            ai_topics: Topics from AI
            keyword_topics: Topics from keyword extraction

        Returns:
            Combined unique list of topics
        """
        all_topics = set()

        # Add all AI topics
        for topic in ai_topics:
            all_topics.add(topic.lower())

        # Add keyword topics, checking for similarity with existing
        for topic in keyword_topics:
            topic_lower = topic.lower()

            # Check if this topic is similar to any existing AI topic
            is_duplicate = False
            for existing in list(all_topics):
                similarity = self.similarity.calculate_similarity(topic_lower, existing)
                if similarity > 0.8:  # Very similar
                    is_duplicate = True
                    break

            if not is_duplicate:
                all_topics.add(topic_lower)

        return list(all_topics)

    def _calculate_frequencies(self, text: str, topics: List[str]) -> Dict[str, int]:
        """
        Calculate how many times each topic appears in the text

        Args:
            text: The source text
            topics: List of topics to count

        Returns:
            Dictionary mapping topic to frequency count
        """
        text_lower = text.lower()
        frequencies = {}

        for topic in topics:
            # Count occurrences (word boundary aware)
            pattern = r"\b" + re.escape(topic) + r"\b"
            count = len(re.findall(pattern, text_lower))
            frequencies[topic] = count

        return frequencies

    def merge_all_sources(
        self, paper_results: List[List[Dict]], transcript_results: List[List[Dict]]
    ) -> List[Dict]:
        """
        Merge topics from multiple papers and transcripts into one prediction

        Args:
            paper_results: List of results from multiple past papers
            transcript_results: List of results from multiple transcripts

        Returns:
            Merged and scored topics
        """
        print("\n" + "=" * 50)
        print("🔄 Merging all sources for final prediction...")
        print("=" * 50)

        topic_scores = {}

        # Process past papers (60% weight)
        for paper in paper_results:
            for topic_info in paper:
                topic = topic_info["topic"]
                score = topic_info["raw_importance"] * 0.6  # 60% weight for papers

                if topic not in topic_scores:
                    topic_scores[topic] = {
                        "paper_score": 0,
                        "transcript_score": 0,
                        "paper_count": 0,
                        "transcript_count": 0,
                        "context": [],
                    }

                topic_scores[topic]["paper_score"] += score
                topic_scores[topic]["paper_count"] += 1

        # Process transcripts (40% weight)
        for transcript in transcript_results:
            for topic_info in transcript:
                topic = topic_info["topic"]
                score = topic_info["emphasis_score"] * 0.4  # 40% weight for transcripts

                if topic not in topic_scores:
                    topic_scores[topic] = {
                        "paper_score": 0,
                        "transcript_score": 0,
                        "paper_count": 0,
                        "transcript_count": 0,
                        "context": [],
                    }

                topic_scores[topic]["transcript_score"] += score
                topic_scores[topic]["transcript_count"] += 1

                if topic_info.get("context"):
                    topic_scores[topic]["context"].append(topic_info["context"])

        # Calculate final scores
        results = []
        for topic, scores in topic_scores.items():
            # Average the scores
            avg_paper = scores["paper_score"] / max(scores["paper_count"], 1)
            avg_transcript = scores["transcript_score"] / max(
                scores["transcript_count"], 1
            )

            # Final probability (0 to 1)
            final_probability = min(1.0, (avg_paper + avg_transcript) / 2)

            # Determine priority category
            if final_probability >= 0.7:
                priority = "🔴 HIGH"
            elif final_probability >= 0.4:
                priority = "🟡 MEDIUM"
            else:
                priority = "🟢 LOW"

            results.append(
                {
                    "topic": topic.title(),  # Capitalize first letter
                    "probability": round(final_probability * 100, 1),  # As percentage
                    "priority": priority,
                    "paper_mentions": scores["paper_count"],
                    "transcript_mentions": scores["transcript_count"],
                    "context": scores["context"][:3],  # Top 3 contexts
                }
            )

        # Sort by probability (highest first)
        results.sort(key=lambda x: x["probability"], reverse=True)

        return results


# Quick test if run directly
if __name__ == "__main__":
    print("🧪 Testing Topic Extractor...")

    # Sample text
    sample_paper = """
    Question 1: Explain inheritance in object-oriented programming.
    Question 2: What is polymorphism and how does it work with virtual functions?
    Question 3: Describe operator overloading with an example.
    """

    sample_transcript = """
    Today we'll cover inheritance. This is very important for the exam.
    Remember that polymorphism allows objects to take many forms.
    Virtual functions are crucial for runtime polymorphism.
    """

    extractor = TopicExtractor()

    # Test paper extraction
    paper_results = extractor.extract_from_past_paper(sample_paper)
    print("\n📄 Paper Results:")
    for r in paper_results[:3]:
        print(f"   - {r['topic']}: frequency {r['frequency']}")

    # Test transcript extraction
    transcript_results = extractor.extract_from_transcript(sample_transcript)
    print("\n📝 Transcript Results:")
    for r in transcript_results[:3]:
        print(f"   - {r['topic']}: emphasis {r['emphasis_score']:.2f}")

    print("\n✅ Topic Extractor ready!")
