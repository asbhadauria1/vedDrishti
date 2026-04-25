"""
VedDrishti - Ollama AI Client
Handles all communication with the local Llama 3.2 model
"""

import ollama
import json
from typing import List, Dict, Any


class OllamaClient:
    """Client for interacting with local Llama 3.2 model"""

    def __init__(self, model_name="llama3.2"):
        """
        Initialize the Ollama client

        Args:
            model_name: Name of the model to use (default: llama3.2)
        """
        self.model_name = model_name
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Try to list models
            response = ollama.list()
            models = [m['model'] for m in response['models']]
            
            # Print available models for debugging
            print(f"📋 Available models: {models}")
            
            # Check if our model is available (check both with and without :latest)
            model_variants = [self.model_name, f"{self.model_name}:latest", self.model_name.replace(':latest', '')]
            
            found_model = None
            for variant in model_variants:
                if variant in models:
                    found_model = variant
                    break
            
            # Also check if any model starts with our model name
            if not found_model:
                for m in models:
                    if m.startswith(self.model_name.replace(':latest', '')):
                        found_model = m
                        break
            
            if found_model:
                self.model_name = found_model  # Use the exact name found
                print(f"✅ Ollama running with {self.model_name}")
                return True
            else:
                print(f"⚠️ Model {self.model_name} not found. Run: ollama pull llama3.2")
                print(f"   Available: {models}")
                return False
                
        except Exception as e:
            print(f"❌ Cannot connect to Ollama. Is it running? Error: {e}")
            return False

    def extract_topics(self, text: str, source_type: str = "paper") -> List[str]:
        """
        Extract topics from text using AI

        Args:
            text: The text to analyze (past paper or transcript)
            source_type: Either "paper" or "transcript"

        Returns:
            List of extracted topics
        """
        if not self.available:
            print("Ollama not available. Returning empty topics.")
            return []

        prompt = f"""
You are analyzing a {source_type} for a university course called COMP2012 (Object-Oriented Programming and Data Structures).

Extract ALL the main topics and concepts from this text. Return ONLY a JSON array of topic names, nothing else.

Example output: ["inheritance", "polymorphism", "virtual functions", "templates", "exception handling"]

Text to analyze:
{text[:3000]}  # Limit text to avoid overwhelming the AI
"""

        try:
            response = ollama.chat(
                model=self.model_name, messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response to get topics
            result = response["message"]["content"]

            # Try to parse as JSON
            try:
                topics = json.loads(result)
                if isinstance(topics, list):
                    return topics
            except:
                # If not JSON, extract topics manually from text
                # Look for patterns like ["topic1", "topic2"]
                import re

                match = re.search(r"\[(.*?)\]", result)
                if match:
                    topics_str = match.group(1)
                    topics = [t.strip().strip("\"'") for t in topics_str.split(",")]
                    return topics

            return []

        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []

    def detect_emphasis(self, transcript_text: str) -> List[Dict]:
        """
        Detect emphasized topics in lecture transcripts

        Args:
            transcript_text: The lecture transcript text

        Returns:
            List of dictionaries with topic, emphasis_score, and context
        """
        if not self.available:
            return []

        prompt = f"""
You are analyzing a university lecture transcript for COMP2012 (OOP & Data Structures).

Find topics that the professor emphasized. Look for:
- Repeated mentions
- Phrases like "this is important", "you must know this", "will be on the exam"
- Time spent explaining a concept

Return ONLY a JSON array of objects with this format:
[
    {{"topic": "inheritance", "emphasis_score": 0.9, "context": "mentioned 5 times, professor said 'crucial for exam'"}},
    {{"topic": "polymorphism", "emphasis_score": 0.8, "context": "spent 15 minutes explaining"}}
]

Transcript:
{transcript_text[:3000]}
"""

        try:
            response = ollama.chat(
                model=self.model_name, messages=[{"role": "user", "content": prompt}]
            )

            result = response["message"]["content"]

            # Parse JSON response
            try:
                emphasized = json.loads(result)
                if isinstance(emphasized, list):
                    return emphasized
            except:
                # Fallback: extract using regex
                import re

                matches = re.findall(
                    r'"topic":\s*"([^"]+)".*?"emphasis_score":\s*([0-9.]+)', result
                )
                return [
                    {"topic": m[0], "emphasis_score": float(m[1]), "context": ""}
                    for m in matches
                ]

            return []

        except Exception as e:
            print(f"Error detecting emphasis: {e}")
            return []

    def parse_grading_review(self, review_text: str) -> Dict:
        """
        Parse course review to extract grading weights and advice

        Args:
            review_text: Student review text

        Returns:
            Dictionary with grading weights and recommendations
        """
        if not self.available:
            return {}

        prompt = f"""
You are analyzing a student course review for COMP2012.

Extract the following information and return as JSON:
1. grading_weights: object with components (Midterm, Final, Homework, Labs, Project) and their percentages
2. advice: key recommendations from the review
3. difficulty: rating from 1-5 (if mentioned)

Review:
{review_text}

Example output:
{{
    "grading_weights": {{"Midterm": 25, "Final": 45, "Homework": 20, "Labs": 10}},
    "advice": "Focus on final exam inheritance and polymorphism",
    "difficulty": 4.2
}}
"""

        try:
            response = ollama.chat(
                model=self.model_name, messages=[{"role": "user", "content": prompt}]
            )

            result = response["message"]["content"]

            # Parse JSON
            try:
                return json.loads(result)
            except:
                return {"raw_response": result}

        except Exception as e:
            print(f"Error parsing review: {e}")
            return {}

    def generate_study_plan(
        self, topics: List[Dict], deadlines: List[Dict]
    ) -> List[Dict]:
        """
        Generate a study plan based on predicted topics and deadlines

        Args:
            topics: List of topics with probability scores
            deadlines: List of upcoming deadlines

        Returns:
            List of study tasks with dates
        """
        if not self.available:
            return []

        prompt = f"""
You are an AI study planner. Create a study schedule based on:

Predicted exam topics (with probability scores):
{json.dumps(topics, indent=2)}

Upcoming deadlines:
{json.dumps(deadlines, indent=2)}

Return a JSON array of study tasks with this format:
[
    {{"topic": "inheritance", "date": "2026-04-25", "priority": 10, "hours": 2}},
    {{"topic": "polymorphism", "date": "2026-04-26", "priority": 9, "hours": 1.5}}
]

Rules:
- Prioritize topics with higher probability scores
- Study high-priority topics BEFORE deadlines
- Spread out topics to avoid cramming
"""

        try:
            response = ollama.chat(
                model=self.model_name, messages=[{"role": "user", "content": prompt}]
            )

            result = response["message"]["content"]

            try:
                return json.loads(result)
            except:
                return []

        except Exception as e:
            print(f"Error generating study plan: {e}")
            return []

    def test_connection(self):
        """Test if Ollama is working properly"""
        if not self.available:
            return False

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "Say 'VedDrishti AI is ready!'"}],
            )
            print(f"✅ AI Test: {response['message']['content']}")
            return True
        except Exception as e:
            print(f"❌ AI Test failed: {e}")
            return False


# Quick test if run directly
if __name__ == "__main__":
    print("🧪 Testing Ollama Client...")
    client = OllamaClient()
    client.test_connection()
