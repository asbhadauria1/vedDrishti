"""
VedDrishti - Unified Review & Course Info Parser
Automatically extracts grading weights, deadlines, and insights from course files
"""

import re
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ollama_client import OllamaClient


class UnifiedParser:
    """Parses both course reviews and course info files automatically"""

    def __init__(self, sample_data_path: str = "sample_data"):
        self.sample_data_path = sample_data_path
        self.ai_client = OllamaClient()

        # Storage for extracted data
        self.grading_weights = {}
        self.deadlines = []
        self.important_topics = []
        self.course_insights = []

    def load_all_data(self):
        """Load and parse all course files automatically"""
        print("\n" + "=" * 60)
        print("📂 LOADING COURSE DATA FROM FILES")
        print("=" * 60)

        # Load course_info.txt
        course_info_path = os.path.join(
            self.sample_data_path, "reviews", "course_info.txt"
        )
        if os.path.exists(course_info_path):
            with open(course_info_path, "r", encoding="utf-8") as f:
                course_info = f.read()
            self._parse_course_info(course_info)
        else:
            print("   ⚠️ course_info.txt not found")

        # Load course review
        review_path = os.path.join(
            self.sample_data_path, "reviews", "COMP2012_course_review.txt"
        )
        if os.path.exists(review_path):
            with open(review_path, "r", encoding="utf-8") as f:
                review_text = f.read()
            self._parse_course_review(review_text)
        else:
            print("   ⚠️ COMP2012_course_review.txt not found")

        print("\n" + "=" * 60)
        print("✅ DATA LOADING COMPLETE")
        print(f"   📊 Grading weights: {len(self.grading_weights)} components")
        print(f"   📅 Deadlines: {len(self.deadlines)} tasks")
        print(f"   💡 Insights: {len(self.course_insights)} items")
        print("=" * 60)

        return self.get_summary()

    def _parse_course_info(self, text: str):
        """Parse course_info.txt for deadlines and grading"""
        print("\n📖 Parsing course_info.txt...")

        # Extract deadlines
        deadline_patterns = [
            r"([A-Z\s]+)\nDue Date: (\d{4}-\d{2}-\d{2})\nEstimated Hours: (\d+)\nGrade Weight: (\d+)%",
            r"([A-Z\s]+)\nDue Date: (\d{4}-\d{2}-\d{2})\nEstimated Hours: (\d+)\nGrade Weight: (\d+)",
        ]

        for pattern in deadline_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                task_name = match[0].strip()
                due_date = match[1]
                hours = int(match[2])
                weight = int(match[3])

                self.deadlines.append(
                    {
                        "task": task_name,
                        "due_date": due_date,
                        "estimated_hours": hours,
                        "weight": weight,
                        "source": "course_info.txt",
                    }
                )
                print(f"   ✅ Found: {task_name} on {due_date} ({weight}%)")

        # Extract grading breakdown
        grading_section = re.search(
            r"GRADING BREAKDOWN(.*?)(?:={10,}|$)", text, re.DOTALL
        )
        if grading_section:
            lines = grading_section.group(1).split("\n")
            for line in lines:
                # Pattern: "Midterm Exam       25%         April 28, 2026"
                match = re.search(r"([A-Za-z\s]+?)\s+(\d+)%\s+", line)
                if match:
                    component = match.group(1).strip()
                    weight = int(match.group(2))
                    if "Midterm" in component:
                        self.grading_weights["Midterm"] = weight
                    elif "Final" in component:
                        self.grading_weights["Final"] = weight
                    elif "Assignment" in component:
                        if "Assignments" not in self.grading_weights:
                            self.grading_weights["Assignments"] = 0
                        self.grading_weights["Assignments"] += weight
                    elif "Lab" in component:
                        self.grading_weights["Labs"] = weight

        # Extract course insights from the bottom section
        insights_section = re.search(
            r"COURSE REVIEW INSIGHTS(.*?)(?:={10,}|$)", text, re.DOTALL
        )
        if insights_section:
            insights = insights_section.group(1).strip().split("\n")
            for insight in insights:
                if insight.strip() and insight.strip()[0] == "-":
                    self.course_insights.append(insight.strip()[1:].strip())

    def _parse_course_review(self, text: str):
        """Parse COMP2012_course_review.txt for additional insights"""
        print("\n📖 Parsing COMP2012_course_review.txt...")

        # Extract grading if not already found
        if not self.grading_weights:
            weight_patterns = [
                r"(Midterm|Final|Homework|Labs|Project)[:\s]*(\d+)%",
                r"(\d+)%\s*(?:for\s+)?(Midterm|Final|Homework|Labs|Project)",
            ]

            for pattern in weight_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        component = (
                            match[0].lower() if match[0].isalpha() else match[1].lower()
                        )
                        weight = int(match[1] if match[1].isdigit() else match[0])

                        if "midterm" in component:
                            self.grading_weights["Midterm"] = max(
                                self.grading_weights.get("Midterm", 0), weight
                            )
                        elif "final" in component:
                            self.grading_weights["Final"] = max(
                                self.grading_weights.get("Final", 0), weight
                            )
                        elif "homework" in component or "assignment" in component:
                            self.grading_weights["Assignments"] = max(
                                self.grading_weights.get("Assignments", 0), weight
                            )
                        elif "lab" in component:
                            self.grading_weights["Labs"] = max(
                                self.grading_weights.get("Labs", 0), weight
                            )

        # Extract important topics mentioned in review
        topic_keywords = [
            "inheritance",
            "polymorphism",
            "virtual",
            "template",
            "exception",
            "bst",
            "avl",
            "hash",
            "stack",
            "queue",
            "constructor",
            "destructor",
        ]

        for topic in topic_keywords:
            if topic in text.lower():
                # Check if it's emphasized
                is_important = any(
                    word in text.lower()
                    for word in ["important", "crucial", "focus", "heavily"]
                )
                self.important_topics.append(
                    {
                        "topic": topic,
                        "importance": "high" if is_important else "medium",
                        "source": "course_review",
                    }
                )

        # Remove duplicates
        seen = set()
        unique_topics = []
        for topic in self.important_topics:
            if topic["topic"] not in seen:
                seen.add(topic["topic"])
                unique_topics.append(topic)
        self.important_topics = unique_topics

        print(f"   ✅ Found {len(self.important_topics)} important topics from review")

    def get_summary(self) -> Dict:
        """Get summary of all extracted data"""
        return {
            "grading_weights": self.grading_weights,
            "deadlines": self.deadlines,
            "important_topics": self.important_topics,
            "course_insights": self.course_insights,
        }

    def get_study_recommendations(self, predictions: List[Dict]) -> Dict:
        """
        Generate unified recommendations combining predictions with course data

        Args:
            predictions: List of predicted topics from Prediction Engine

        Returns:
            Dictionary with comprehensive study recommendations
        """
        recommendations = {
            "effort_allocation": {},
            "priority_topics": [],
            "deadline_warnings": [],
            "study_schedule": [],
        }

        # Effort allocation based on grading weights
        if self.grading_weights:
            total_weight = sum(self.grading_weights.values())
            for component, weight in self.grading_weights.items():
                percentage = (
                    (weight / total_weight) * 100 if total_weight > 0 else weight
                )
                if percentage >= 40:
                    recommendations["effort_allocation"][
                        component
                    ] = f"🔥 HIGH PRIORITY - Spend {min(60, int(percentage) + 15)}% of time"
                elif percentage >= 20:
                    recommendations["effort_allocation"][
                        component
                    ] = f"📘 MEDIUM PRIORITY - Spend {percentage // 2}% of time"
                else:
                    recommendations["effort_allocation"][
                        component
                    ] = f"⚡ LOW PRIORITY - Minimum effort"

        # Priority topics from predictions
        if predictions:
            high_priority = [p for p in predictions if p.get("priority") == "🔴 HIGH"][
                :5
            ]
            recommendations["priority_topics"] = high_priority

        # Deadline warnings
        if self.deadlines:
            from datetime import datetime

            today = datetime.now()
            upcoming = [
                d
                for d in self.deadlines
                if datetime.strptime(d["due_date"], "%Y-%m-%d") > today
            ]
            upcoming = sorted(upcoming, key=lambda x: x["due_date"])[:5]

            for deadline in upcoming:
                recommendations["deadline_warnings"].append(
                    {
                        "task": deadline["task"],
                        "date": deadline["due_date"],
                        "weight": deadline.get("weight", 0),
                        "hours": deadline.get("estimated_hours", 0),
                    }
                )

        return recommendations


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Unified Parser...")

    parser = UnifiedParser()
    data = parser.load_all_data()

    print("\n📊 Extracted Data:")
    print(f"   Grading: {data['grading_weights']}")
    print(f"   Deadlines: {len(data['deadlines'])}")
    for d in data["deadlines"][:3]:
        print(f"      - {d['task']}: {d['due_date']}")
    print(f"   Important Topics: {len(data['important_topics'])}")

    print("\n✅ Unified Parser ready!")
