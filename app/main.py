"""
VedDrishti - Main Application
Complete AI-powered exam prediction engine
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.prediction_engine import PredictionEngine
from database.db_integration import DatabaseIntegrator


class VedDrishti:
    """Main application class"""

    def __init__(self, course_code: str = "COMP2012"):
        self.course_code = course_code
        self.predictor = PredictionEngine()
        self.db = DatabaseIntegrator()

        print(f"\n{'='*60}")
        print(f"🎓 VEDDRISHTI - AI Exam Prediction Engine")
        print(f"📚 Course: {course_code}")
        print(f"{'='*60}")

    def load_sample_data(self):
        """Load sample data for demonstration"""

        print("\n📂 Loading sample data...")

        # Sample past papers
        papers = [
            {
                "text": """
                Question 1: Explain the concept of inheritance in object-oriented programming. 
                Provide an example using C++.
                
                Question 2: What is polymorphism? How do virtual functions enable polymorphism?
                
                Question 3: Describe operator overloading. When would you use it?
                
                Question 4: What are templates? Compare function templates and class templates.
                """,
                "year": 2024,
            },
            {
                "text": """
                Question 1: Discuss encapsulation and data hiding. Why are they important?
                
                Question 2: Explain constructors and destructors. What is the rule of three?
                
                Question 3: What are friend functions? When should they be used?
                
                Question 4: Describe exception handling in C++ with examples.
                """,
                "year": 2023,
            },
            {
                "text": """
                Question 1: Compare inheritance and composition. When to use each?
                
                Question 2: Explain dynamic binding versus static binding.
                
                Question 3: What are abstract classes? How do they differ from interfaces?
                
                Question 4: Describe the STL containers: vector, list, map.
                """,
                "year": 2022,
            },
        ]

        # Sample transcripts
        transcripts = [
            {
                "text": """
                Professor: Today we're covering inheritance. This is extremely important for the exam.
                You absolutely must understand how derived classes inherit from base classes.
                We'll spend extra time on this because it appears on every exam.
                
                Next, polymorphism. Virtual functions are the key to polymorphism in C++.
                Remember: virtual functions enable runtime polymorphism.
                This is crucial - expect questions on this.
                
                Finally, templates. I won't spend too much time here, but you should know the basics.
                """,
                "lecture_num": 1,
            },
            {
                "text": """
                Professor: Let's continue with exception handling. This is important for writing robust code.
                You need to know try, catch, and throw.
                
                Now, operator overloading. This is good to know but not as critical as inheritance.
                We'll cover the basic syntax.
                
                Remember, the final exam will focus heavily on inheritance and polymorphism.
                """,
                "lecture_num": 2,
            },
        ]

        return papers, transcripts

    def run_prediction(self, papers: list, transcripts: list):
        """Run the prediction pipeline"""

        # Step 1: Process past papers
        print("\n" + "=" * 60)
        print("📚 STEP 1: Analyzing Past Papers")
        print("=" * 60)
        paper_results = self.predictor.process_past_papers(papers)

        # Step 2: Process transcripts
        print("\n" + "=" * 60)
        print("📝 STEP 2: Analyzing Lecture Transcripts")
        print("=" * 60)
        transcript_results = self.predictor.process_transcripts(transcripts)

        # Step 3: Generate predictions
        print("\n" + "=" * 60)
        print("🔮 STEP 3: Generating Predictions")
        print("=" * 60)
        predictions = self.predictor.generate_predictions(
            paper_results, transcript_results
        )

        return predictions

    def save_results(self, predictions: list, transcripts: list):
        """Save predictions and transcripts to databases"""

        print("\n" + "=" * 60)
        print("💾 STEP 4: Saving to Databases")
        print("=" * 60)

        # Save topics to SQLite
        self.db.save_topics(self.course_code, predictions)

        # Save prediction history
        self.db.save_prediction_history(self.course_code, predictions)

        # Save transcripts to MongoDB
        for transcript in transcripts:
            self.db.save_transcript(
                self.course_code, transcript.get("lecture_num", 1), transcript["text"]
            )

        print("\n✅ All data saved successfully!")

    def display_results(self):
        """Display predictions and recommendations"""
        self.predictor.display_predictions()

        # Get study recommendations
        recommendations = self.predictor.get_study_recommendations()

        print("\n" + "=" * 60)
        print("📚 STUDY RECOMMENDATIONS")
        print("=" * 60)

        for key, value in recommendations.items():
            if key != "focus_topics":
                print(f"\n{key.replace('_', ' ').title()}:")
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"   • {k}: {v}")
                elif isinstance(value, list):
                    for item in value:
                        print(f"   • {item}")
                else:
                    print(f"   {value}")

    def run(self):
        """Run the complete VedDrishti pipeline"""

        # Load sample data
        papers, transcripts = self.load_sample_data()

        # Run prediction
        predictions = self.run_prediction(papers, transcripts)

        # Save results
        self.save_results(predictions, transcripts)

        # Display results
        self.display_results()

        # Get accuracy tracking
        accuracy = self.db.get_prediction_accuracy(self.course_code)
        print("\n" + "=" * 60)
        print("📊 PREDICTION ACCURACY TRACKING")
        print("=" * 60)
        print(f"   Total predictions made: {accuracy['total_predictions']}")
        print(
            f"   Average accuracy: {accuracy['average_accuracy']:.1%}"
            if accuracy["average_accuracy"]
            else "   No accuracy data yet (after exam, mark actual occurrences)"
        )

        # Close connections
        self.db.close()

        print("\n" + "=" * 60)
        print("🎉 VedDrishti execution complete!")
        print("=" * 60)


if __name__ == "__main__":
    # Run VedDrishti
    app = VedDrishti(course_code="COMP2012")
    app.run()
