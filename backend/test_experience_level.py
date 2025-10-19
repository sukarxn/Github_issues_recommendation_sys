"""
Test suite for experience level extraction accuracy.
Tests the embedding-based experience level detection system.
"""

import pytest
from sentence_transformers import SentenceTransformer
from core import extract_experience_level_embeddings, EXPERIENCE_LEVEL_REFERENCES
import shutil
import os


class TestExperienceLevelExtraction:
    """Test suite for experience level extraction using embeddings."""
    
    @pytest.fixture
    def model(self):
        """Load the sentence transformer model."""
        return SentenceTransformer('all-MiniLM-L6-v2')
    
    # ============== BEGINNER PROFILES ==============
    
    def test_beginner_new_programmer(self, model):
        """Test detection of beginner - new programmer."""
        profile = "I am a beginner programmer just learning to code. I know basic Python syntax."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "beginner", f"Expected 'beginner', got '{level}'"
    
    def test_beginner_bootcamp_graduate(self, model):
        """Test detection of beginner - bootcamp graduate."""
        profile = "I just finished a coding bootcamp and am starting to learn web development."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "beginner", f"Expected 'beginner', got '{level}'"
    
    def test_beginner_first_language(self, model):
        """Test detection of beginner - first language learner."""
        profile = "I am learning Python for the first time. I'm comfortable with basic syntax and data structures."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "beginner", f"Expected 'beginner', got '{level}'"
    
    def test_beginner_student(self, model):
        """Test detection of beginner - computer science student."""
        profile = "I am a student starting my coding journey. I'm enjoying solving simple programming problems."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "beginner", f"Expected 'beginner', got '{level}'"
    
    def test_beginner_less_than_year(self, model):
        """Test detection of beginner - less than a year experience."""
        profile = "I have been coding for less than a year and I'm looking for beginner-friendly projects to contribute to."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "beginner", f"Expected 'beginner', got '{level}'"
    
    # ============== INTERMEDIATE PROFILES ==============
    
    def test_intermediate_2_years_experience(self, model):
        """Test detection of intermediate - 2 years experience."""
        profile = "I have shipped production code and managed deployed applications. I build REST APIs with multiple endpoints and handle database queries."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "intermediate", f"Expected 'intermediate', got '{level}'"
    
    def test_intermediate_production_projects(self, model):
        """Test detection of intermediate - production experience."""
        profile = "I refactor legacy code and improve existing codebases. I implement unit tests and integration tests in my projects."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "intermediate", f"Expected 'intermediate', got '{level}'"
    
    def test_intermediate_fullstack(self, model):
        """Test detection of intermediate - full-stack developer."""
        profile = "I develop full-stack features from backend to frontend. I understand design patterns like MVC and apply them to my work."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "intermediate", f"Expected 'intermediate', got '{level}'"
    
    def test_intermediate_open_source(self, model):
        """Test detection of intermediate - open-source contributor."""
        profile = "I contribute to open-source repositories and maintain feature branches. I use Git effectively with pull requests and code reviews."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "intermediate", f"Expected 'intermediate', got '{level}'"
    
    def test_intermediate_oop(self, model):
        """Test detection of intermediate - OOP understanding."""
        profile = "I write object-oriented code with proper encapsulation and inheritance. I optimize query performance and debug memory leaks in applications."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "intermediate", f"Expected 'intermediate', got '{level}'"
    
    # ============== ADVANCED PROFILES ==============
    
    def test_advanced_senior_engineer(self, model):
        """Test detection of advanced - senior engineer."""
        profile = "I architect distributed microservices handling millions of transactions. I lead engineering teams and make critical infrastructure decisions."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "advanced", f"Expected 'advanced', got '{level}'"
    
    def test_advanced_performance_optimization(self, model):
        """Test detection of advanced - performance optimization specialist."""
        profile = "I optimize performance for high-traffic systems and handle scale. I design and implement distributed systems with consensus algorithms."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "advanced", f"Expected 'advanced', got '{level}'"
    
    def test_advanced_microservices(self, model):
        """Test detection of advanced - microservices architect."""
        profile = "I build microservices with message queues and event-driven architecture. I manage Kubernetes clusters and DevOps infrastructure at enterprise scale."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "advanced", f"Expected 'advanced', got '{level}'"
    
    def test_advanced_mentor(self, model):
        """Test detection of advanced - mentor and interviewer."""
        profile = "I mentor senior developers and conduct architectural reviews. I maintain core libraries and frameworks used by thousands."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "advanced", f"Expected 'advanced', got '{level}'"
    
    def test_advanced_open_source_maintainer(self, model):
        """Test detection of advanced - open-source core maintainer."""
        profile = "I am an expert in system architecture and technical strategy. I contribute to large open-source projects as a core maintainer."
        level = extract_experience_level_embeddings(profile, model)
        assert level == "advanced", f"Expected 'advanced', got '{level}'"
    
    # ============== EDGE CASES ==============
    
    def test_empty_profile(self, model):
        """Test with empty profile - should default to 'any'."""
        profile = ""
        level = extract_experience_level_embeddings(profile, model)
        assert level == "any", f"Expected 'any' for empty profile, got '{level}'"
    
    def test_none_profile(self, model):
        """Test with None profile - should default to 'any'."""
        level = extract_experience_level_embeddings(None, model)
        assert level == "any", f"Expected 'any' for None profile, got '{level}'"
    
    def test_mixed_experience_profile(self, model):
        """Test with mixed experience levels - should pick the best match."""
        # This profile has both beginner and intermediate signals
        profile = "I just started learning but I also have some experience building APIs. I'm comfortable with basic web development."
        level = extract_experience_level_embeddings(profile, model)
        # Should lean towards beginner since it emphasizes "just started"
        assert level in ["beginner", "intermediate"], f"Expected beginner or intermediate, got '{level}'"
    
    def test_similarity_scores(self, model):
        """Test that similarity scores are computed correctly."""
        # Beginner profile from references
        beginner_profile = EXPERIENCE_LEVEL_REFERENCES['beginner'][0]
        level = extract_experience_level_embeddings(beginner_profile, model)
        assert level == "beginner", f"Reference beginner profile should be detected as beginner, got '{level}'"
        
        # Intermediate profile from references
        intermediate_profile = EXPERIENCE_LEVEL_REFERENCES['intermediate'][0]
        level = extract_experience_level_embeddings(intermediate_profile, model)
        assert level == "intermediate", f"Reference intermediate profile should be detected as intermediate, got '{level}'"
        
        # Advanced profile from references
        advanced_profile = EXPERIENCE_LEVEL_REFERENCES['advanced'][0]
        level = extract_experience_level_embeddings(advanced_profile, model)
        assert level == "advanced", f"Reference advanced profile should be detected as advanced, got '{level}'"


class TestExperienceLevelAccuracy:
    """Test overall accuracy of the experience level extraction system."""
    
    @pytest.fixture
    def model(self):
        """Load the sentence transformer model."""
        return SentenceTransformer('all-MiniLM-L6-v2')
    
    def test_reference_examples_accuracy(self, model):
        """Verify that reference examples are correctly classified."""
        expected = {
            'beginner': 10,
            'intermediate': 10,
            'advanced': 10,
        }
        
        results = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0,
        }
        
        for level, examples in EXPERIENCE_LEVEL_REFERENCES.items():
            for example in examples:
                detected_level = extract_experience_level_embeddings(example, model)
                if detected_level == level:
                    results[level] += 1
        
        print(f"\n✅ Reference Examples Classification Accuracy:")
        print(f"   Beginner: {results['beginner']}/{expected['beginner']}")
        print(f"   Intermediate: {results['intermediate']}/{expected['intermediate']}")
        print(f"   Advanced: {results['advanced']}/{expected['advanced']}")
        
        # We expect high accuracy (at least 80%) on reference examples
        for level in ['beginner', 'intermediate', 'advanced']:
            accuracy = (results[level] / expected[level]) * 100
            assert accuracy >= 80, f"{level} accuracy is only {accuracy}%, expected >= 80%"


@pytest.fixture(scope="session", autouse=True)
def clear_cache():
    """Clear the embedding cache before running tests."""
    cache_dir = '/tmp/github_issues_cache'
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    yield
    # Optionally clear after tests too
    # shutil.rmtree(cache_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
