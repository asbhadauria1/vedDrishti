"""
VedDrishti - Prediction Engine
Master component that combines all AI modules to generate exam predictions
"""

import json
from typing import List, Dict, Optional
from datetime import datetime

# Handle imports
try:
    from .topic_extractor import TopicExtractor
    from .emphasis_detector import EmphasisDetector
    from .ollama_client import OllamaClient
except ImportError:
    from topic_extractor import TopicExtractor
    from emphasis_detector import EmphasisDetector
    from ollama_client import OllamaClient


class PredictionEngine:
    """Main prediction engine for VedDrishti"""

    def __init__(self):
        """Initialize all AI components"""
        print("\n" + "=" * 60)
        print("🚀 VEDDRISHTI PREDICTION ENGINE INITIALIZING...")
        print("=" * 60)

        self.topic_extractor = TopicExtractor()
        self.emphasis_detector = EmphasisDetector()
        self.ai_client = OllamaClient()

        self.predictions = []

    def process_past_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Process multiple past papers

        Args:
            papers: List of dicts with 'text' and 'year' keys

        Returns:
            List of results from each paper
        """
        print("\n📚 PROCESSING PAST PAPERS...")
        print("-" * 40)

        results = []
        for i, paper in enumerate(papers):
            text = paper.get("text", "")
            year = paper.get("year", None)

            if text:
                result = self.topic_extractor.extract_from_past_paper(text, year)
                results.append(result)

        print(f"✅ Processed {len(results)} past papers")
        return results

    def process_transcripts(self, transcripts: List[Dict]) -> List[Dict]:
        """
        Process multiple lecture transcripts

        Args:
            transcripts: List of dicts with 'text' and 'lecture_num' keys

        Returns:
            List of results from each transcript
        """
        print("\n📝 PROCESSING TRANSCRIPTS...")
        print("-" * 40)

        results = []
        for i, transcript in enumerate(transcripts):
            text = transcript.get("text", "")
            lecture_num = transcript.get("lecture_num", i + 1)

            if text:
                # Do full emphasis analysis
                emphasis_result = self.emphasis_detector.analyze_transcript(text)

                # Also extract topics
                topics = self.topic_extractor.extract_from_transcript(text, lecture_num)

                results.append({"topics": topics, "emphasis": emphasis_result})

        print(f"✅ Processed {len(results)} transcripts")
        return results

    def generate_predictions(
        self, paper_results: List[List[Dict]], transcript_results: List[Dict]
    ) -> List[Dict]:
        """
        Generate final predictions by merging all sources

        Args:
            paper_results: Results from past papers
            transcript_results: Results from transcripts

        Returns:
            List of predicted topics with probabilities
        """
        print("\n🔮 GENERATING FINAL PREDICTIONS...")
        print("-" * 40)

        # Extract just the topic lists from transcript results
        transcript_topic_lists = [
            t["topics"] for t in transcript_results if "topics" in t
        ]

        # Merge using topic extractor's merge function
        merged = self.topic_extractor.merge_all_sources(
            paper_results, transcript_topic_lists
        )

        self.predictions = merged
        return merged

    def display_predictions(self):
        """Pretty print the predictions"""
        if not self.predictions:
            print("No predictions available. Run generate_predictions first.")
            return

        print("\n" + "=" * 60)
        print("📊 EXAM PREDICTIONS")
        print("=" * 60)

        # Group by priority
        high = [p for p in self.predictions if p["priority"] == "🔴 HIGH"]
        medium = [p for p in self.predictions if p["priority"] == "🟡 MEDIUM"]
        low = [p for p in self.predictions if p["priority"] == "🟢 LOW"]

        if high:
            print("\n🔴 HIGH PROBABILITY (Study First)")
            print("-" * 40)
            for p in high:
                print(f"   {p['topic']}: {p['probability']}%")
                print(
                    f"      (appears in {p['paper_mentions']} papers, {p['transcript_mentions']} transcripts)"
                )

        if medium:
            print("\n🟡 MEDIUM PROBABILITY")
            print("-" * 40)
            for p in medium[:5]:  # Show top 5
                print(f"   {p['topic']}: {p['probability']}%")

        if low:
            print("\n🟢 LOW PROBABILITY (Deprioritize)")
            print("-" * 40)
            for p in low[:3]:  # Show top 3
                print(f"   {p['topic']}: {p['probability']}%")

        print("\n" + "=" * 60)

    def get_study_recommendations(self) -> Dict:
        """
        Generate study recommendations based on predictions

        Returns:
            Dictionary with study recommendations
        """
        if not self.predictions:
            return {"error": "No predictions available"}

        # Get top 5 high probability topics
        high_topics = [p for p in self.predictions if p["priority"] == "🔴 HIGH"][:5]

        # Get grading weights (from SQL - will integrate later)
        grading_weights = {"Final": 45, "Midterm": 25, "Homework": 20, "Labs": 10}

        recommendations = {
            "focus_topics": high_topics,
            "grading_weights": grading_weights,
            "effort_allocation": {
                "Final": "50% of study time",
                "Midterm": "25% of study time",
                "Homework": "Minimum effort (10% weight)",
                "Labs": "Minimum effort (10% weight)",
            },
            "study_plan": [
                f"Day 1-2: {high_topics[0]['topic'] if high_topics else 'Review high priority topics'}",
                f"Day 3-4: {high_topics[1]['topic'] if len(high_topics) > 1 else 'Review medium priority topics'}",
                "Day 5: Practice problems",
                "Day 6: Review weak areas",
                "Day 7: Final review",
            ],
        }

        return recommendations


# Quick test with sample data
if __name__ == "__main__":
    print("🧪 Testing Prediction Engine...")

    # Sample data
    sample_papers = [
        {
            "text": "Question: Explain inheritance and polymorphism. What are virtual functions?",
            "year": 2024,
        },
        {
            "text": "Discuss operator overloading. When would you use friend functions?",
            "year": 2023,
        },
    ]

    sample_transcripts = [
        {
            "text": "Inheritance is very important for the exam. Virtual functions are crucial. You must know polymorphism.",
            "lecture_num": 1,
        }
    ]

    # Run prediction
    engine = PredictionEngine()
    paper_results = engine.process_past_papers(sample_papers)
    transcript_results = engine.process_transcripts(sample_transcripts)
    predictions = engine.generate_predictions(paper_results, transcript_results)
    engine.display_predictions()

    # Get recommendations
    recommendations = engine.get_study_recommendations()
    print("\n📚 STUDY RECOMMENDATIONS:")
    print(json.dumps(recommendations, indent=2))

    print("\n✅ Prediction Engine ready!")
