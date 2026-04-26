"""
VedDrishti - MongoDB Initialization Script
Sets up collections and indexes for transcripts and embeddings
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Your MongoDB connection string
# IMPORTANT: Replace <password> with your actual password!
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")

# Database name
DB_NAME = "veddrishti"


def get_mongo_connection():
    """Establish connection to MongoDB Atlas"""
    try:
        client = MongoClient(MONGO_URI)
        # Test the connection
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas successfully!")
        return client
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None


def setup_collections():
    """Create collections and indexes for VedDrishti"""

    client = get_mongo_connection()
    if not client:
        return

    db = client[DB_NAME]

    # =============================================
    # 1. TRANSCRIPTS COLLECTION
    # Stores full lecture transcripts with emphasis detection
    # =============================================
    print("\n📝 Setting up 'transcripts' collection...")

    # Create collection (it's created automatically when we insert)
    transcripts = db.transcripts

    # Create indexes for faster queries
    transcripts.create_index("course_code")
    transcripts.create_index("lecture_date")
    transcripts.create_index([("topics_discussed", 1)])

    print("   ✅ transcripts collection ready")

    # =============================================
    # 2. EMBEDDINGS COLLECTION
    # Stores AI vector embeddings for topic similarity
    # =============================================
    print("\n🔢 Setting up 'embeddings' collection...")

    embeddings = db.embeddings

    # Create index on topic for fast lookup
    embeddings.create_index("topic_name")
    embeddings.create_index("course_code")

    print("   ✅ embeddings collection ready")

    # =============================================
    # 3. COURSE_REVIEWS COLLECTION
    # Stores student reviews and grading information
    # =============================================
    print("\n📋 Setting up 'course_reviews' collection...")

    reviews = db.course_reviews

    reviews.create_index("course_code")
    reviews.create_index("helpful_count")

    print("   ✅ course_reviews collection ready")

    # =============================================
    # 4. PREDICTION_RESULTS COLLECTION
    # Stores AI prediction outputs
    # =============================================
    print("\n🔮 Setting up 'prediction_results' collection...")

    predictions = db.prediction_results

    predictions.create_index("course_code")
    predictions.create_index("prediction_date")

    print("   ✅ prediction_results collection ready")

    # =============================================
    # Insert sample data
    # =============================================
    print("\n📊 Inserting sample data...")

    # Sample transcript entry (for demonstration)
    sample_transcript = {
        "course_code": "COMP2012",
        "lecture_number": 1,
        "lecture_date": "2026-02-15",
        "full_text": "Today we will cover inheritance... this is very important for the exam...",
        "emphasized_phrases": [
            {
                "phrase": "inheritance is very important",
                "count": 3,
                "context": "exam preparation",
            },
            {
                "phrase": "virtual functions",
                "count": 2,
                "context": "polymorphism discussion",
            },
        ],
        "topics_discussed": ["inheritance", "polymorphism", "classes"],
        "processed": False,
    }

    # Insert only if collection is empty
    if transcripts.count_documents({}) == 0:
        transcripts.insert_one(sample_transcript)
        print("   ✅ Sample transcript added")

    # Sample course review
    sample_review = {
        "course_code": "COMP2012",
        "semester": "Spring 2025",
        "review_text": "Midterm 25%, Final 45%. The final focused heavily on inheritance and polymorphism. Homework was 20% but very time consuming.",
        "grading_weights": {"Midterm": 25, "Final": 45, "Homework": 20, "Labs": 10},
        "difficulty_rating": 4.2,
        "helpful_count": 45,
    }

    if reviews.count_documents({}) == 0:
        reviews.insert_one(sample_review)
        print("   ✅ Sample review added")

    print("\n" + "=" * 50)
    print("✅ MongoDB setup complete!")
    print("=" * 50)

    # Display summary
    print("\n📊 Collections created:")
    print(f"   - transcripts: {transcripts.count_documents({})} documents")
    print(f"   - embeddings: {embeddings.count_documents({})} documents")
    print(f"   - course_reviews: {reviews.count_documents({})} documents")
    print(f"   - prediction_results: {predictions.count_documents({})} documents")

    client.close()


def test_mongodb():
    """Simple test to verify MongoDB operations"""

    client = get_mongo_connection()
    if not client:
        return False

    db = client[DB_NAME]

    # Test insert and query
    test_collection = db.test
    test_doc = {"test": "VedDrishti connection test", "timestamp": "2026-04-25"}

    test_collection.insert_one(test_doc)
    result = test_collection.find_one({"test": "VedDrishti connection test"})

    if result:
        print("\n✅ MongoDB read/write test passed!")
        test_collection.delete_one({"_id": result["_id"]})
        client.close()
        return True
    else:
        print("\n❌ MongoDB test failed!")
        client.close()
        return False


if __name__ == "__main__":
    print("🚀 Setting up MongoDB for VedDrishti...")
    print("=" * 50)
    setup_collections()
    print("\n🧪 Running test...")
    test_mongodb()
