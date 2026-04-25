"""
VedDrishti - Database Integration Module
Connects AI predictions with SQLite and MongoDB
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient

# Check if running in Docker
IN_DOCKER = os.environ.get("DOCKER_ENV", "false").lower() == "true"

if IN_DOCKER:
    MONGO_URI = "mongodb://mongodb:27017/"
    POSTGRES_HOST = "postgres"
    OLLAMA_HOST = "http://ollama:11434"
else:
    MONGO_URI = "mongodb://localhost:27017/"
    POSTGRES_HOST = "localhost"
    OLLAMA_HOST = "http://localhost:11434"

# Database paths
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "veddrishti.db")

# MongoDB connection (update with your connection string)
# IMPORTANT: Replace with your actual MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://abhadauria2006_db_user:GT5y082HON0hlXcj@cluster0.j3rpdku.mongodb.net/?appName=Cluster0"
MONGO_DB_NAME = "veddrishti"


class DatabaseIntegrator:
    """Handles all database operations for VedDrishti"""

    def __init__(self):
        """Initialize connections to both databases"""
        print("🔗 Initializing Database Integrator...")
        
        # SQLite connection
        self.sql_conn = sqlite3.connect(DB_PATH)
        self.sql_cursor = self.sql_conn.cursor()
        print("   ✅ SQLite connected")
        
        # MongoDB connection
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            self.mongo_db = self.mongo_client[MONGO_DB_NAME]
            # Test connection
            self.mongo_client.admin.command('ping')
            print("   ✅ MongoDB connected")
        except Exception as e:
            print(f"   ⚠️ MongoDB connection failed: {e}")
            self.mongo_client = None

    # =============================================
    # SQLITE OPERATIONS
    # =============================================

    def save_topics(self, course_code: str, topics: List[Dict]) -> int:
        """
        Save extracted topics to SQLite
        
        Args:
            course_code: Course code (e.g., COMP2012)
            topics: List of topic dictionaries with probabilities
        
        Returns:
            Number of topics saved
        """
        # Get course ID
        self.sql_cursor.execute("SELECT id FROM courses WHERE course_code = ?", (course_code,))
        course = self.sql_cursor.fetchone()
        
        if not course:
            print(f"   ❌ Course {course_code} not found in database")
            return 0
        
        course_id = course[0]
        saved_count = 0
        
        for topic_data in topics:
            topic_name = topic_data.get('topic', '')
            probability = topic_data.get('probability', 0) / 100  # Convert from percentage
            
            # Check if topic already exists
            self.sql_cursor.execute(
                "SELECT id FROM topics WHERE course_id = ? AND topic_name = ?",
                (course_id, topic_name)
            )
            existing = self.sql_cursor.fetchone()
            
            if existing:
                # Update existing topic
                self.sql_cursor.execute("""
                    UPDATE topics 
                    SET probability_score = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (probability, existing[0]))
            else:
                # Insert new topic - use 'both' as source since it comes from AI prediction
                self.sql_cursor.execute("""
                    INSERT INTO topics (course_id, topic_name, probability_score, source)
                    VALUES (?, ?, ?, ?)
                """, (course_id, topic_name, probability, 'both'))
            
            saved_count += 1
        
        self.sql_conn.commit()
        print(f"   ✅ Saved {saved_count} topics to SQLite")
        return saved_count

    def save_prediction_history(self, course_code: str, predictions: List[Dict]) -> int:
        """
        Save prediction results for future accuracy tracking

        Args:
            course_code: Course code
            predictions: List of prediction dictionaries

        Returns:
            Number of predictions saved
        """
        self.sql_cursor.execute(
            "SELECT id FROM courses WHERE course_code = ?", (course_code,)
        )
        course = self.sql_cursor.fetchone()

        if not course:
            print(f"   ❌ Course {course_code} not found")
            return 0

        course_id = course[0]
        today = datetime.now().strftime("%Y-%m-%d")
        saved_count = 0

        for pred in predictions:
            topic_name = pred.get("topic", "")
            probability = pred.get("probability", 0) / 100

            self.sql_cursor.execute(
                """
                INSERT INTO prediction_history 
                (course_id, prediction_date, topic_name, predicted_probability, accuracy_score)
                VALUES (?, ?, ?, ?, ?)
            """,
                (course_id, today, topic_name, probability, None),
            )
            saved_count += 1

        self.sql_conn.commit()
        print(f"   ✅ Saved {saved_count} predictions to history")
        return saved_count

    def save_study_plan(self, course_code: str, study_plan: List[Dict]) -> int:
        """
        Save generated study plan to SQLite
        
        Args:
            course_code: Course code
            study_plan: List of study tasks with dates and topics
        
        Returns:
            Number of tasks saved
        """
        self.sql_cursor.execute("SELECT id FROM courses WHERE course_code = ?", (course_code,))
        course = self.sql_cursor.fetchone()
        
        if not course:
            print(f"   ❌ Course {course_code} not found")
            return 0
        
        course_id = course[0]
        saved_count = 0
        
        for task in study_plan:
            topic_name = task.get('topic', '')
            scheduled_date = task.get('date', datetime.now().strftime('%Y-%m-%d'))
            priority = task.get('priority', 5)
            
            # Ensure priority is an integer between 1-10
            try:
                priority_int = int(priority)
                if priority_int < 1:
                    priority_int = 1
                if priority_int > 10:
                    priority_int = 10
            except (ValueError, TypeError):
                priority_int = 5
            
            hours = task.get('hours', 1)
            
            # Find topic ID
            self.sql_cursor.execute(
                "SELECT id FROM topics WHERE course_id = ? AND topic_name = ?",
                (course_id, topic_name)
            )
            topic = self.sql_cursor.fetchone()
            
            if topic:
                topic_id = topic[0]
                self.sql_cursor.execute("""
                    INSERT INTO study_plan (topic_id, scheduled_date, priority_score, study_minutes)
                    VALUES (?, ?, ?, ?)
                """, (topic_id, scheduled_date, priority_int, hours * 60))
                saved_count += 1
        
        self.sql_conn.commit()
        print(f"   ✅ Saved {saved_count} study tasks to SQLite")
        return saved_count

    def get_course_id(self, course_code: str) -> Optional[int]:
        """Get course ID from course code"""
        self.sql_cursor.execute(
            "SELECT id FROM courses WHERE course_code = ?", (course_code,)
        )
        result = self.sql_cursor.fetchone()
        return result[0] if result else None

    # =============================================
    # MONGODB OPERATIONS
    # =============================================

    def save_transcript(
        self,
        course_code: str,
        lecture_num: int,
        transcript_text: str,
        emphasis_data: Dict = None,
    ) -> bool:
        """
        Save transcript and emphasis analysis to MongoDB

        Args:
            course_code: Course code
            lecture_num: Lecture number
            transcript_text: Full transcript text
            emphasis_data: Emphasis analysis results

        Returns:
            Success status
        """
        if not self.mongo_client:
            print("   ⚠️ MongoDB not available")
            return False

        collection = self.mongo_db.transcripts

        document = {
            "course_code": course_code,
            "lecture_number": lecture_num,
            "lecture_date": datetime.now().strftime("%Y-%m-%d"),
            "full_text": transcript_text,
            "processed": True,
            "processed_date": datetime.now().isoformat(),
        }

        if emphasis_data:
            document["emphasized_phrases"] = emphasis_data.get("cues_found", [])
            document["repeated_topics"] = emphasis_data.get("repeated_topics", {})
            document["final_scores"] = emphasis_data.get("final_scores", [])

        result = collection.insert_one(document)
        print(f"   ✅ Saved transcript to MongoDB (id: {result.inserted_id})")
        return True

    def save_embeddings(
        self, course_code: str, topic: str, embedding_vector: list
    ) -> bool:
        """
        Save topic embeddings for similarity search

        Args:
            course_code: Course code
            topic: Topic name
            embedding_vector: The embedding vector (list of floats)

        Returns:
            Success status
        """
        if not self.mongo_client:
            return False

        collection = self.mongo_db.embeddings

        document = {
            "course_code": course_code,
            "topic_name": topic,
            "embedding": embedding_vector,
            "created_at": datetime.now().isoformat(),
        }

        collection.update_one(
            {"course_code": course_code, "topic_name": topic},
            {"$set": document},
            upsert=True,
        )
        return True

    def get_transcripts(self, course_code: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve transcripts for a course

        Args:
            course_code: Course code
            limit: Maximum number of transcripts to return

        Returns:
            List of transcript documents
        """
        if not self.mongo_client:
            return []

        collection = self.mongo_db.transcripts
        results = list(
            collection.find({"course_code": course_code}, {"_id": 0}).limit(limit)
        )

        print(f"   📄 Retrieved {len(results)} transcripts from MongoDB")
        return results

    def get_prediction_accuracy(self, course_code: str) -> Dict:
        """
        Calculate prediction accuracy for a course

        Args:
            course_code: Course code

        Returns:
            Dictionary with accuracy statistics
        """
        self.sql_cursor.execute(
            """
            SELECT 
                COUNT(*) as total_predictions,
                AVG(accuracy_score) as avg_accuracy
            FROM prediction_history ph
            JOIN courses c ON ph.course_id = c.id
            WHERE c.course_code = ? AND accuracy_score IS NOT NULL
        """,
            (course_code,),
        )

        result = self.sql_cursor.fetchone()

        return {
            "total_predictions": result[0] if result else 0,
            "average_accuracy": result[1] if result and result[1] else 0,
        }

    def close(self):
        """Close database connections"""
        self.sql_conn.close()
        if self.mongo_client:
            self.mongo_client.close()
        print("🔒 Database connections closed")


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Database Integration...")

    db = DatabaseIntegrator()

    # Test SQLite query
    db.sql_cursor.execute("SELECT * FROM courses")
    courses = db.sql_cursor.fetchall()
    print(f"📚 Courses in database: {courses}")

    # Test MongoDB connection
    if db.mongo_client:
        print("✅ MongoDB is connected and ready")

    db.close()
    print("\n✅ Database Integrator ready!")
