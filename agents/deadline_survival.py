"""
VedDrishti - Deadline Survival Agent
Uses predictions from Prediction Engine to create intelligent study schedules
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


class DeadlineSurvivalAgent:
    """Intelligent deadline manager that uses topic predictions"""

    def __init__(self, deadlines: List[Dict] = None):
        """
        Initialize with deadlines from course_info.txt

        Args:
            deadlines: List of deadline dictionaries from UnifiedParser
        """
        self.deadlines = deadlines or []
        self.workload_spikes = []
        self.study_plan = []
        self.predictions = []

    def set_predictions(self, predictions: List[Dict]):
        """
        Set predictions from Prediction Engine

        Args:
            predictions: List of predicted topics with probabilities
        """
        self.predictions = predictions
        print(f"📊 Received {len(predictions)} predictions from Prediction Engine")

    def detect_workload_spikes(self, window_days: int = 7) -> List[Dict]:
        """
        Detect periods with multiple deadlines close together

        Args:
            window_days: Number of days to consider as a spike window

        Returns:
            List of workload spikes
        """
        if not self.deadlines:
            return []

        # Sort deadlines by date
        sorted_deadlines = sorted(self.deadlines, key=lambda x: x["due_date"])

        spikes = []

        for i, deadline in enumerate(sorted_deadlines):
            current_date = datetime.strptime(deadline["due_date"], "%Y-%m-%d")

            # Check deadlines within the window
            deadlines_in_window = []
            for other in sorted_deadlines:
                other_date = datetime.strptime(other["due_date"], "%Y-%m-%d")
                days_diff = abs((other_date - current_date).days)
                if days_diff <= window_days:
                    deadlines_in_window.append(other)

            # Remove duplicates
            deadlines_in_window = list(
                {d["due_date"]: d for d in deadlines_in_window}.values()
            )

            # If 2 or more deadlines in window, it's a spike
            if len(deadlines_in_window) >= 2:
                spike = {
                    "start_date": min(d["due_date"] for d in deadlines_in_window),
                    "end_date": max(d["due_date"] for d in deadlines_in_window),
                    "deadline_count": len(deadlines_in_window),
                    "deadlines": deadlines_in_window,
                    "severity": "HIGH" if len(deadlines_in_window) >= 3 else "MEDIUM",
                }

                # Avoid duplicate spikes
                if spike not in spikes:
                    spikes.append(spike)

        self.workload_spikes = spikes
        return spikes

    def generate_adaptive_study_plan(self, study_days_ahead: int = 30) -> List[Dict]:
        """
        Generate study plan that prioritizes based on:
        1. Topic probability (from Prediction Engine)
        2. Upcoming deadlines
        3. Workload spikes

        Args:
            study_days_ahead: How many days to plan for

        Returns:
            List of study tasks with dates
        """
        print("\n" + "=" * 60)
        print("📚 GENERATING ADAPTIVE STUDY PLAN")
        print("=" * 60)

        if not self.predictions:
            print("⚠️ No predictions available. Run Prediction Engine first.")
            return []

        # Sort topics by probability (highest first)
        sorted_topics = sorted(
            self.predictions, key=lambda x: x.get("probability", 0), reverse=True
        )

        # Separate by priority
        high_priority = [t for t in sorted_topics if t.get("priority") == "🔴 HIGH"][:5]
        medium_priority = [
            t for t in sorted_topics if t.get("priority") == "🟡 MEDIUM"
        ][:5]
        low_priority = [t for t in sorted_topics if t.get("priority") == "🟢 LOW"][:3]

        print(f"\n🎯 Topic Prioritization:")
        print(f"   🔴 HIGH priority: {len(high_priority)} topics")
        print(f"   🟡 MEDIUM priority: {len(medium_priority)} topics")
        print(f"   🟢 LOW priority: {len(low_priority)} topics")

        # Detect workload spikes
        spikes = self.detect_workload_spikes()

        if spikes:
            print(f"\n⚠️ Workload Spikes Detected:")
            for spike in spikes:
                print(
                    f"   • {spike['deadline_count']} deadlines from {spike['start_date']} to {spike['end_date']}"
                )

        # Identify busy periods (dates with deadlines or spikes)
        busy_dates = set()

        # Add all deadline dates
        for deadline in self.deadlines:
            busy_dates.add(deadline["due_date"])
            # Add buffer days
            due_date = datetime.strptime(deadline["due_date"], "%Y-%m-%d")
            for offset in [-1, 1]:
                buffer_date = due_date + timedelta(days=offset)
                busy_dates.add(buffer_date.strftime("%Y-%m-%d"))

        # Add spike periods
        for spike in spikes:
            start = datetime.strptime(spike["start_date"], "%Y-%m-%d")
            end = datetime.strptime(spike["end_date"], "%Y-%m-%d")
            current = start
            while current <= end:
                busy_dates.add(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)

        # Generate study plan
        study_plan = []
        study_date = datetime.now()
        topics_assigned = 0
        all_topics = high_priority + medium_priority + low_priority

        print(f"\n📅 Generating schedule for next {study_days_ahead} days...")

        # First, schedule HIGH priority topics on non-busy days BEFORE deadlines
        for topic in high_priority:
            # Find a good date
            assigned = False
            check_date = datetime.now()
            days_checked = 0

            while not assigned and days_checked < study_days_ahead:
                date_str = check_date.strftime("%Y-%m-%d")

                # Check if this date is busy
                is_busy = date_str in busy_dates

                # Also check if this date is after any important deadlines
                has_upcoming_deadline = False
                for deadline in self.deadlines[:3]:  # Check first 3 deadlines
                    deadline_date = datetime.strptime(deadline["due_date"], "%Y-%m-%d")
                    if check_date > deadline_date - timedelta(days=2):
                        has_upcoming_deadline = True

                if not is_busy and not has_upcoming_deadline:
                    study_plan.append(
                        {
                            "topic": topic["topic"],
                            "date": date_str,
                            "priority": topic["probability"],
                            "priority_level": "HIGH",
                            "hours": 3 if topic["probability"] >= 80 else 2,
                            "reason": f"Exam probability: {topic['probability']}% - Study before deadlines",
                        }
                    )
                    assigned = True
                    topics_assigned += 1

                check_date += timedelta(days=1)
                days_checked += 1

        # Then schedule MEDIUM priority topics
        for topic in medium_priority:
            assigned = False
            check_date = datetime.now()
            days_checked = 0

            while not assigned and days_checked < study_days_ahead:
                date_str = check_date.strftime("%Y-%m-%d")
                is_busy = date_str in busy_dates

                if not is_busy:
                    study_plan.append(
                        {
                            "topic": topic["topic"],
                            "date": date_str,
                            "priority": topic["probability"],
                            "priority_level": "MEDIUM",
                            "hours": 2,
                            "reason": f"Exam probability: {topic['probability']}%",
                        }
                    )
                    assigned = True
                    topics_assigned += 1

                check_date += timedelta(days=1)
                days_checked += 1

        # Finally schedule LOW priority topics (can be during busy periods)
        for topic in low_priority:
            study_plan.append(
                {
                    "topic": topic["topic"],
                    "date": (datetime.now() + timedelta(days=len(study_plan))).strftime(
                        "%Y-%m-%d"
                    ),
                    "priority": topic["probability"],
                    "priority_level": "LOW",
                    "hours": 1,
                    "reason": f"Exam probability: {topic['probability']}% - Low priority, can study anytime",
                }
            )

        self.study_plan = study_plan
        print(f"   ✅ Generated {len(study_plan)} study tasks")

        return study_plan

    def get_survival_report(self) -> Dict:
        """
        Generate comprehensive survival report

        Returns:
            Dictionary with warnings, advice, and schedule
        """
        report = {
            "deadlines": self.deadlines,
            "workload_spikes": self.workload_spikes,
            "study_plan": self.study_plan,
            "warnings": [],
            "advice": [],
        }

        # Add spike warnings
        for spike in self.workload_spikes:
            report["warnings"].append(
                f"⚠️ WORKLOAD SPIKE: {spike['deadline_count']} deadlines between {spike['start_date']} and {spike['end_date']}"
            )

        # Add advice based on predictions
        if self.predictions:
            high_topics = [
                p for p in self.predictions if p.get("priority") == "🔴 HIGH"
            ]
            if high_topics:
                topics_str = ", ".join([t["topic"] for t in high_topics[:3]])
                report["advice"].append(
                    f"🎯 FOCUS FIRST: {topics_str} (high exam probability)"
                )

        # Add deadline advice
        if self.deadlines:
            upcoming = sorted(self.deadlines, key=lambda x: x["due_date"])[:2]
            for d in upcoming:
                report["advice"].append(
                    f"📅 Prepare for {d['task']} by {d['due_date']} ({d.get('weight', 0)}% of grade)"
                )

        if not self.workload_spikes:
            report["advice"].append(
                "✅ Workload looks manageable. Follow the study plan above."
            )

        return report

    def display_report(self):
        """Pretty print the survival report"""
        report = self.get_survival_report()

        print("\n" + "=" * 60)
        print("📅 DEADLINE SURVIVAL REPORT")
        print("=" * 60)

        if report["warnings"]:
            print("\n⚠️ WARNINGS:")
            for w in report["warnings"]:
                print(f"   {w}")

        if report["deadlines"]:
            print("\n📋 UPCOMING DEADLINES:")
            for d in sorted(report["deadlines"], key=lambda x: x["due_date"])[:5]:
                print(f"   • {d['task']}: {d['due_date']} ({d.get('weight', 0)}%)")

        if report["study_plan"]:
            print("\n📚 ADAPTIVE STUDY PLAN:")
            print("   (Prioritizing high-probability exam topics)")
            for task in report["study_plan"][:10]:
                print(
                    f"   • {task['date']}: {task['priority_level']} - {task['topic']} ({task['hours']} hours)"
                )
                print(f"     → {task['reason']}")

        if report["advice"]:
            print("\n💡 SURVIVAL ADVICE:")
            for a in report["advice"]:
                print(f"   {a}")

        print("\n" + "=" * 60)


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Deadline Survival Agent...")

    # Sample deadlines (as would come from course_info.txt)
    sample_deadlines = [
        {
            "task": "Assignment 1",
            "due_date": "2026-04-20",
            "estimated_hours": 5,
            "weight": 15,
        },
        {
            "task": "Midterm Exam",
            "due_date": "2026-04-28",
            "estimated_hours": 15,
            "weight": 25,
        },
        {
            "task": "Assignment 2",
            "due_date": "2026-05-05",
            "estimated_hours": 8,
            "weight": 20,
        },
        {
            "task": "Final Project",
            "due_date": "2026-05-22",
            "estimated_hours": 15,
            "weight": 30,
        },
        {
            "task": "Final Exam",
            "due_date": "2026-05-26",
            "estimated_hours": 20,
            "weight": 45,
        },
    ]

    # Sample predictions (as would come from Prediction Engine)
    sample_predictions = [
        {"topic": "Inheritance", "probability": 85, "priority": "🔴 HIGH"},
        {"topic": "Polymorphism", "probability": 82, "priority": "🔴 HIGH"},
        {"topic": "Virtual Functions", "probability": 78, "priority": "🔴 HIGH"},
        {"topic": "Templates", "probability": 45, "priority": "🟡 MEDIUM"},
        {"topic": "Exception Handling", "probability": 42, "priority": "🟡 MEDIUM"},
        {"topic": "Operator Overloading", "probability": 25, "priority": "🟢 LOW"},
    ]

    agent = DeadlineSurvivalAgent(sample_deadlines)
    agent.set_predictions(sample_predictions)
    agent.generate_adaptive_study_plan(study_days_ahead=20)
    agent.display_report()

    print("\n✅ Deadline Survival Agent ready!")
