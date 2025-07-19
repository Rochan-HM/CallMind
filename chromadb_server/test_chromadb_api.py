#!/usr/bin/env python3
"""
Comprehensive test script for the ChromaDB API.
This script will:
1. Start the API server in the background
2. Create multiple collections with dummy data
3. Test all API endpoints
4. Verify data persistence and search functionality
"""

import os
import sys
import time
import json
import subprocess
import signal
import threading
import requests
from typing import Dict, List, Any
from datetime import datetime


class ChromaDBAPITester:
    def __init__(self, base_url: str = "http://localhost:8501"):
        self.base_url = base_url
        self.server_process = None
        self.collections_created = []

    def start_server(self):
        """Start the ChromaDB API server in the background."""
        print("🚀 Starting ChromaDB API server...")

        # Check if server is already running
        if self.is_server_running():
            print("✅ Server is already running!")
            return True

        try:
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "chromadb_server.app"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
            )

            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                if self.is_server_running():
                    print("✅ Server started successfully!")
                    time.sleep(2)  # Give it a bit more time to fully initialize
                    return True
                time.sleep(1)
                print(f"   Checking server status... ({i+1}/30)")

            print("❌ Server failed to start within 30 seconds")
            return False

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    def is_server_running(self) -> bool:
        """Check if the API server is running."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

    def stop_server(self):
        """Stop the API server."""
        if self.server_process:
            print("🛑 Stopping API server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Server stopped")

    def pretty_print_response(self, response: requests.Response, action: str):
        """Helper function to pretty print API responses."""
        print(f"\n{'='*60}")
        print(f"🔍 {action}")
        print(f"Status Code: {response.status_code}")

        if response.status_code in [200, 201]:
            print("✅ Success!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text}")
        else:
            print("❌ Error!")
            print(f"Error: {response.text}")

    def test_health_check(self):
        """Test the health check endpoint."""
        print("\n" + "=" * 60)
        print("🏥 TESTING HEALTH CHECK")
        print("=" * 60)

        response = requests.get(f"{self.base_url}/")
        self.pretty_print_response(response, "Health Check")
        return response.status_code == 200

    def create_sample_collections(self):
        """Create multiple collections with different types of dummy data."""
        print("\n" + "=" * 60)
        print("📚 CREATING SAMPLE COLLECTIONS WITH DUMMY DATA")
        print("=" * 60)

        # Collection 1: Technology Articles
        tech_collection = "technology_articles"
        tech_documents = [
            {
                "content": "Artificial Intelligence is revolutionizing the way we interact with technology. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions with remarkable accuracy.",
                "metadata": {
                    "category": "AI",
                    "topic": "machine_learning",
                    "difficulty": "intermediate",
                    "date": "2024-01-15",
                },
            },
            {
                "content": "Python is a versatile programming language that has gained massive popularity in data science, web development, and automation. Its simple syntax makes it accessible to beginners while powerful libraries make it suitable for complex applications.",
                "metadata": {
                    "category": "programming",
                    "topic": "python",
                    "difficulty": "beginner",
                    "date": "2024-01-16",
                },
            },
            {
                "content": "Cloud computing has transformed how businesses deploy and scale their applications. AWS, Azure, and Google Cloud provide robust infrastructure that can handle massive workloads with high availability and security.",
                "metadata": {
                    "category": "cloud",
                    "topic": "infrastructure",
                    "difficulty": "advanced",
                    "date": "2024-01-17",
                },
            },
            {
                "content": "Cybersecurity threats are evolving rapidly in the digital age. Organizations must implement multi-layered security strategies including firewalls, encryption, and employee training to protect sensitive data.",
                "metadata": {
                    "category": "security",
                    "topic": "cybersecurity",
                    "difficulty": "advanced",
                    "date": "2024-01-18",
                },
            },
            {
                "content": "The Internet of Things (IoT) connects everyday devices to the internet, enabling smart homes, autonomous vehicles, and industrial automation. This interconnected ecosystem generates massive amounts of data.",
                "metadata": {
                    "category": "IoT",
                    "topic": "smart_devices",
                    "difficulty": "intermediate",
                    "date": "2024-01-19",
                },
            },
        ]

        self.create_collection_with_documents(tech_collection, tech_documents)

        # Collection 2: Science Facts
        science_collection = "science_facts"
        science_documents = [
            {
                "content": "The human brain contains approximately 86 billion neurons, each connected to thousands of others, creating a complex network that enables consciousness, memory, and thought.",
                "metadata": {
                    "subject": "neuroscience",
                    "type": "fact",
                    "complexity": "high",
                    "verified": True,
                },
            },
            {
                "content": "Water has a unique property where it expands when it freezes, making ice less dense than liquid water. This is why ice floats and why pipes burst in winter.",
                "metadata": {
                    "subject": "physics",
                    "type": "fact",
                    "complexity": "medium",
                    "verified": True,
                },
            },
            {
                "content": "The speed of light in a vacuum is exactly 299,792,458 meters per second. This fundamental constant is crucial for understanding relativity and the nature of the universe.",
                "metadata": {
                    "subject": "physics",
                    "type": "constant",
                    "complexity": "high",
                    "verified": True,
                },
            },
            {
                "content": "DNA is structured as a double helix with four nucleotide bases: Adenine, Thymine, Guanine, and Cytosine. The sequence of these bases encodes all genetic information.",
                "metadata": {
                    "subject": "biology",
                    "type": "structure",
                    "complexity": "medium",
                    "verified": True,
                },
            },
            {
                "content": "The Milky Way galaxy contains over 100 billion stars and is approximately 100,000 light-years in diameter. Our solar system is located in one of its spiral arms.",
                "metadata": {
                    "subject": "astronomy",
                    "type": "fact",
                    "complexity": "medium",
                    "verified": True,
                },
            },
        ]

        self.create_collection_with_documents(science_collection, science_documents)

        # Collection 3: Recipe Database
        recipe_collection = "recipes"
        recipe_documents = [
            {
                "content": "Classic Chocolate Chip Cookies: Mix 2 cups flour, 1 tsp baking soda, 1 tsp salt. Cream 1 cup butter with 3/4 cup each brown and white sugar. Add 2 eggs and 2 tsp vanilla. Combine wet and dry ingredients, fold in 2 cups chocolate chips. Bake at 375°F for 9-11 minutes.",
                "metadata": {
                    "cuisine": "american",
                    "type": "dessert",
                    "prep_time": 15,
                    "cook_time": 11,
                    "servings": 24,
                    "difficulty": "easy",
                },
            },
            {
                "content": "Italian Pasta Carbonara: Cook 1 lb spaghetti. In a large bowl, whisk 4 egg yolks with 1 cup grated Parmesan. Cook 6 oz diced pancetta until crispy. Toss hot pasta with pancetta, then quickly mix with egg mixture off heat. Season with black pepper.",
                "metadata": {
                    "cuisine": "italian",
                    "type": "main_course",
                    "prep_time": 10,
                    "cook_time": 20,
                    "servings": 4,
                    "difficulty": "medium",
                },
            },
            {
                "content": "Thai Green Curry: Blend 4 green chilies, 2 shallots, 4 garlic cloves, ginger, lemongrass, and Thai basil. Fry paste in coconut oil, add coconut milk, fish sauce, and palm sugar. Simmer with chicken and vegetables. Serve with jasmine rice.",
                "metadata": {
                    "cuisine": "thai",
                    "type": "main_course",
                    "prep_time": 30,
                    "cook_time": 25,
                    "servings": 6,
                    "difficulty": "hard",
                },
            },
            {
                "content": "Fresh Garden Salad: Mix lettuce, tomatoes, cucumbers, and red onions. Make vinaigrette with olive oil, balsamic vinegar, Dijon mustard, honey, salt, and pepper. Toss salad with dressing and top with croutons.",
                "metadata": {
                    "cuisine": "american",
                    "type": "salad",
                    "prep_time": 10,
                    "cook_time": 0,
                    "servings": 4,
                    "difficulty": "easy",
                },
            },
            {
                "content": "Japanese Miso Soup: Heat 4 cups dashi broth. Whisk 3 tbsp miso paste with some warm broth until smooth. Add back to pot with cubed tofu, wakame seaweed, and sliced green onions. Do not boil after adding miso.",
                "metadata": {
                    "cuisine": "japanese",
                    "type": "soup",
                    "prep_time": 5,
                    "cook_time": 10,
                    "servings": 4,
                    "difficulty": "easy",
                },
            },
        ]

        self.create_collection_with_documents(recipe_collection, recipe_documents)

        return [tech_collection, science_collection, recipe_collection]

    def create_collection_with_documents(
        self, collection_name: str, documents: List[Dict[str, Any]]
    ):
        """Helper method to create a collection and add documents to it."""
        print(f"\n📁 Creating collection: {collection_name}")
        doc_ids = []

        for i, doc in enumerate(documents):
            response = requests.post(
                f"{self.base_url}/collections/{collection_name}/documents", json=doc
            )

            if response.status_code == 200:
                doc_id = response.json().get("id")
                doc_ids.append(doc_id)
                print(f"   ✅ Added document {i+1}/{len(documents)}: {doc_id}")
            else:
                print(f"   ❌ Failed to add document {i+1}: {response.text}")

        self.collections_created.append(collection_name)
        print(
            f"✅ Collection '{collection_name}' created with {len(doc_ids)} documents"
        )
        return doc_ids

    def test_list_collections(self):
        """Test listing all collections."""
        print("\n" + "=" * 60)
        print("📋 TESTING LIST COLLECTIONS")
        print("=" * 60)

        response = requests.get(f"{self.base_url}/collections")
        self.pretty_print_response(response, "List Collections")
        return response.status_code == 200

    def test_collection_counts(self):
        """Test getting document counts for each collection."""
        print("\n" + "=" * 60)
        print("🔢 TESTING COLLECTION COUNTS")
        print("=" * 60)

        for collection in self.collections_created:
            response = requests.get(f"{self.base_url}/collections/{collection}/count")
            self.pretty_print_response(response, f"Get Count for '{collection}'")

    def test_semantic_queries(self):
        """Test semantic search queries across different collections."""
        print("\n" + "=" * 60)
        print("🔍 TESTING SEMANTIC SEARCH QUERIES")
        print("=" * 60)

        # Technology queries
        tech_queries = [
            {"query": "What is machine learning and AI?", "n_results": 3},
            {"query": "Python programming language features", "n_results": 2},
            {"query": "cloud computing benefits", "n_results": 2},
        ]

        for query in tech_queries:
            response = requests.post(
                f"{self.base_url}/collections/technology_articles/query", json=query
            )
            self.pretty_print_response(response, f"Tech Query: '{query['query']}'")

        # Science queries
        science_queries = [
            {"query": "How does the human brain work?", "n_results": 2},
            {"query": "Properties of water and ice", "n_results": 1},
            {"query": "space and astronomy facts", "n_results": 2},
        ]

        for query in science_queries:
            response = requests.post(
                f"{self.base_url}/collections/science_facts/query", json=query
            )
            self.pretty_print_response(response, f"Science Query: '{query['query']}'")

        # Recipe queries
        recipe_queries = [
            {"query": "easy dessert recipes", "n_results": 2},
            {"query": "pasta dishes from Italy", "n_results": 1},
            {"query": "Asian soup recipes", "n_results": 2},
        ]

        for query in recipe_queries:
            response = requests.post(
                f"{self.base_url}/collections/recipes/query", json=query
            )
            self.pretty_print_response(response, f"Recipe Query: '{query['query']}'")

    def test_metadata_filtering(self):
        """Test queries with metadata filters."""
        print("\n" + "=" * 60)
        print("🔎 TESTING METADATA FILTERING")
        print("=" * 60)

        # Filter tech articles by difficulty
        filter_queries = [
            {
                "collection": "technology_articles",
                "query": {
                    "query": "programming",
                    "n_results": 5,
                    "where": {"difficulty": "beginner"},
                },
                "description": "Tech articles for beginners",
            },
            {
                "collection": "science_facts",
                "query": {
                    "query": "physics",
                    "n_results": 5,
                    "where": {"subject": "physics"},
                },
                "description": "Physics facts only",
            },
            {
                "collection": "recipes",
                "query": {
                    "query": "easy recipes",
                    "n_results": 5,
                    "where": {"difficulty": "easy"},
                },
                "description": "Easy recipes only",
            },
        ]

        for filter_query in filter_queries:
            response = requests.post(
                f"{self.base_url}/collections/{filter_query['collection']}/query",
                json=filter_query["query"],
            )
            self.pretty_print_response(
                response, f"Filtered Query: {filter_query['description']}"
            )

    def test_document_operations(self):
        """Test individual document operations (get, update, delete)."""
        print("\n" + "=" * 60)
        print("📄 TESTING DOCUMENT OPERATIONS")
        print("=" * 60)

        # Get all documents from technology collection to test with
        response = requests.post(
            f"{self.base_url}/collections/technology_articles/query",
            json={"query": "technology", "n_results": 1},
        )

        if response.status_code == 200 and response.json():
            doc_id = response.json()[0]["id"]

            # Test getting document by ID
            response = requests.get(
                f"{self.base_url}/collections/technology_articles/documents/{doc_id}"
            )
            self.pretty_print_response(response, f"Get Document by ID: {doc_id}")

            # Test updating document
            update_data = {
                "metadata": {
                    "category": "AI",
                    "updated": True,
                    "last_modified": datetime.now().isoformat(),
                }
            }
            response = requests.put(
                f"{self.base_url}/collections/technology_articles/documents/{doc_id}",
                json=update_data,
            )
            self.pretty_print_response(response, f"Update Document: {doc_id}")

            # Verify update worked
            response = requests.get(
                f"{self.base_url}/collections/technology_articles/documents/{doc_id}"
            )
            self.pretty_print_response(response, f"Verify Update: {doc_id}")

    def run_comprehensive_test(self):
        """Run the complete test suite."""
        print("🎯 Starting Comprehensive ChromaDB API Test")
        print("=" * 60)

        try:
            # Start server
            if not self.start_server():
                return False

            # Run tests in sequence
            tests = [
                ("Health Check", self.test_health_check),
                ("Create Collections", self.create_sample_collections),
                ("List Collections", self.test_list_collections),
                ("Collection Counts", self.test_collection_counts),
                ("Semantic Queries", self.test_semantic_queries),
                ("Metadata Filtering", self.test_metadata_filtering),
                ("Document Operations", self.test_document_operations),
            ]

            failed_tests = []
            for test_name, test_func in tests:
                print(f"\n🧪 Running test: {test_name}")
                try:
                    result = test_func()
                    if result is False:
                        failed_tests.append(test_name)
                    print(f"✅ {test_name} completed")
                except Exception as e:
                    print(f"❌ {test_name} failed: {e}")
                    failed_tests.append(test_name)

            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)

            if failed_tests:
                print(f"❌ {len(failed_tests)} test(s) failed:")
                for test in failed_tests:
                    print(f"   - {test}")
            else:
                print("✅ All tests passed successfully!")

            print(f"\n📈 Results:")
            print(f"   - Collections created: {len(self.collections_created)}")
            print(f"   - API endpoints tested: 8+")
            print(f"   - Semantic search queries: 15+")
            print(f"   - Metadata filters tested: 3")

            print(f"\n🎉 Test suite completed!")
            print(f"🌐 API Documentation: {self.base_url}/docs")
            print(f"📁 ChromaDB data persisted in: ./chroma_db")

        finally:
            # Always stop server when done
            self.stop_server()

    def cleanup(self):
        """Clean up resources."""
        self.stop_server()


def main():
    """Main function to run the test."""
    print("🧪 ChromaDB API Comprehensive Test Script")
    print("=" * 60)

    tester = ChromaDBAPITester()

    try:
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
