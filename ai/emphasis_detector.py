"""
VedDrishti - Emphasis Detector Module
Specialized in detecting professor emphasis from lecture transcripts
"""

import re
from typing import List, Dict, Tuple
from collections import Counter

# Handle imports
try:
    from .ollama_client import OllamaClient
except ImportError:
    from ollama_client import OllamaClient


class EmphasisDetector:
    """Detects emphasized topics in lecture transcripts"""

    def __init__(self):
        """Initialize the emphasis detector"""
        print("🎯 Initializing Emphasis Detector...")
        self.ai_client = OllamaClient()

        # Verbal emphasis cues to look for
        self.high_emphasis_phrases = [
            "this is important",
            "very important",
            "crucial",
            "critical",
            "you must know",
            "will be on the exam",
            "exam question",
            "remember this",
            "key concept",
            "essential",
            "fundamental",
            "pay attention",
            "this will appear",
            "guaranteed to be on",
        ]

        self.medium_emphasis_phrases = [
            "you should know",
            "good to know",
            "note that",
            "keep in mind",
            "typically appears",
            "common question",
            "frequently asked",
        ]

        self.low_emphasis_phrases = [
            "just for reference",
            "optional",
            "if you have time",
            "not required",
            "beyond scope",
            "for your interest",
        ]

    def detect_cue_phrases(self, text: str) -> List[Dict]:
        """
        Detect emphasis cue phrases in transcript text

        Args:
            text: Transcript text

        Returns:
            List of detected cues with positions and emphasis level
        """
        text_lower = text.lower()
        cues = []

        # Check for high emphasis phrases
        for phrase in self.high_emphasis_phrases:
            if phrase in text_lower:
                # Find the sentence containing this phrase
                sentences = re.split(r"[.!?]+", text)
                for sentence in sentences:
                    if phrase in sentence.lower():
                        cues.append(
                            {
                                "phrase": phrase,
                                "context": sentence.strip(),
                                "emphasis_level": "high",
                                "score": 0.9,
                            }
                        )
                        break

        # Check for medium emphasis phrases
        for phrase in self.medium_emphasis_phrases:
            if phrase in text_lower:
                sentences = re.split(r"[.!?]+", text)
                for sentence in sentences:
                    if phrase in sentence.lower():
                        cues.append(
                            {
                                "phrase": phrase,
                                "context": sentence.strip(),
                                "emphasis_level": "medium",
                                "score": 0.6,
                            }
                        )
                        break

        # Check for low emphasis phrases
        for phrase in self.low_emphasis_phrases:
            if phrase in text_lower:
                sentences = re.split(r"[.!?]+", text)
                for sentence in sentences:
                    if phrase in sentence.lower():
                        cues.append(
                            {
                                "phrase": phrase,
                                "context": sentence.strip(),
                                "emphasis_level": "low",
                                "score": 0.2,
                            }
                        )
                        break

        return cues

    def extract_topics_from_cues(self, cues: List[Dict]) -> Dict[str, float]:
        """
        Extract topics from emphasis cues

        Args:
            cues: List of detected cue phrases with context

        Returns:
            Dictionary mapping topics to emphasis scores
        """
        topic_scores = {}

        for cue in cues:
            context = cue["context"]
            emphasis_score = cue["score"]

            # Extract potential topic words from context
            # Look for capitalized words or words after "this/that"
            patterns = [
                r"(?:this|that|the concept of|the idea of) (\w+)",
                r"([A-Z][a-z]+(?: [A-Z][a-z]+)*)",  # Capitalized phrases
            ]

            for pattern in patterns:
                matches = re.findall(pattern, context)
                for match in matches:
                    topic = match.lower()
                    if len(topic) > 3:  # Ignore very short words
                        if topic not in topic_scores:
                            topic_scores[topic] = 0
                        topic_scores[topic] = max(topic_scores[topic], emphasis_score)

        return topic_scores

    def detect_repetition(self, text: str, min_occurrences: int = 3) -> Dict[str, int]:
        """
        Detect topics that are repeated multiple times

        Args:
            text: Transcript text
            min_occurrences: Minimum times a topic appears to count

        Returns:
            Dictionary mapping topics to occurrence count
        """
        text_lower = text.lower()

        # Common COMP2012 topics to check for repetition
        common_topics = [
            "inheritance",
            "polymorphism",
            "encapsulation",
            "abstraction",
            "virtual function",
            "dynamic binding",
            "template",
            "exception",
            "constructor",
            "destructor",
            "operator overloading",
            "friend",
            "multiple inheritance",
            "abstract class",
            "interface",
        ]

        repetition = {}
        for topic in common_topics:
            # Count occurrences
            pattern = r"\b" + re.escape(topic) + r"s?\b"
            count = len(re.findall(pattern, text_lower))

            if count >= min_occurrences:
                repetition[topic] = count

        # Sort by count
        repetition = dict(sorted(repetition.items(), key=lambda x: x[1], reverse=True))

        return repetition

    def analyze_transcript(self, transcript_text: str) -> Dict:
        """
        Complete analysis of a transcript

        Args:
            transcript_text: Full transcript text

        Returns:
            Dictionary with all emphasis analysis results
        """
        print("🔍 Analyzing transcript for emphasis...")

        # 1. Detect cue phrases
        cues = self.detect_cue_phrases(transcript_text)
        print(f"   📍 Found {len(cues)} emphasis cues")

        # 2. Extract topics from cues
        cue_topics = self.extract_topics_from_cues(cues)

        # 3. Detect repetition
        repeated_topics = self.detect_repetition(transcript_text)

        # 4. Use AI for deeper analysis
        ai_emphasis = self.ai_client.detect_emphasis(transcript_text)

        # Combine all sources
        final_topics = {}

        # Add cue-based topics (weight: 0.3)
        for topic, score in cue_topics.items():
            final_topics[topic] = final_topics.get(topic, 0) + score * 0.3

        # Add repeated topics (weight: 0.3)
        for topic, count in repeated_topics.items():
            score = min(1.0, count / 10)  # Normalize
            final_topics[topic] = final_topics.get(topic, 0) + score * 0.3

        # Add AI-detected topics (weight: 0.4)
        for item in ai_emphasis:
            topic = item.get("topic", "").lower()
            score = item.get("emphasis_score", 0.5)
            if topic:
                final_topics[topic] = final_topics.get(topic, 0) + score * 0.4

        # Normalize scores to 0-1
        if final_topics:
            max_score = max(final_topics.values())
            if max_score > 0:
                final_topics = {k: v / max_score for k, v in final_topics.items()}

        # Prepare results
        results = []
        for topic, score in sorted(
            final_topics.items(), key=lambda x: x[1], reverse=True
        ):
            results.append(
                {
                    "topic": topic.title(),
                    "emphasis_score": round(score, 2),
                    "priority": (
                        "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW"
                    ),
                }
            )

        return {
            "cues_found": cues,
            "repeated_topics": repeated_topics,
            "ai_emphasis": ai_emphasis,
            "final_scores": results,
        }


# Quick test if run directly
if __name__ == "__main__":
    print("🧪 Testing Emphasis Detector...")

    # Sample transcript
    sample_transcript = """
    Professor: Today we're going to cover inheritance. This is a very important concept.
    You must know inheritance for the exam. It appears in almost every exam.
    
    Next, let's talk about polymorphism. Virtual functions are how we implement polymorphism.
    Remember this - virtual functions are crucial.
    
    Finally, templates. This is just for your reference, not required for the exam.
    """

    detector = EmphasisDetector()
    result = detector.analyze_transcript(sample_transcript)

    print("\n📊 Final Emphasis Scores:")
    for topic in result["final_scores"][:5]:
        print(f"   {topic['topic']}: {topic['emphasis_score']} ({topic['priority']})")

    print("\n✅ Emphasis Detector ready!")
