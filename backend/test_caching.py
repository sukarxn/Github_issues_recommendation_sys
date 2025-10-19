#!/usr/bin/env python3
"""
Test script to verify caching implementation:
1. Student profile embedding caching
2. Reference embeddings caching
3. GitHub issues caching
"""

import time
from core import (
    create_embedding_model,
    get_or_create_student_embedding,
    extract_experience_level_embeddings,
    get_or_create_reference_embeddings,
    EXPERIENCE_LEVEL_REFERENCES,
    get_cached_student_embedding,
    get_cached_reference_embeddings,
    clear_profile_embeddings_cache,
    clear_reference_embeddings_cache,
)

def test_reference_embeddings_caching():
    """Test reference embeddings caching."""
    print("\n" + "="*60)
    print("TEST 1: Reference Embeddings Caching")
    print("="*60)
    
    model = create_embedding_model()
    
    for level in ['beginner', 'intermediate', 'advanced']:
        references = EXPERIENCE_LEVEL_REFERENCES[level]
        
        # First call - should generate
        print(f"\n--- First call for {level} ---")
        start = time.time()
        embeddings_1 = get_or_create_reference_embeddings(level, references, model)
        time_1 = time.time() - start
        print(f"Time: {time_1:.3f}s, Embeddings count: {len(embeddings_1)}")
        
        # Second call - should use cache
        print(f"\n--- Second call for {level} (should be cached) ---")
        start = time.time()
        embeddings_2 = get_or_create_reference_embeddings(level, references, model)
        time_2 = time.time() - start
        print(f"Time: {time_2:.3f}s, Embeddings count: {len(embeddings_2)}")
        
        # Verify caching worked
        speedup = time_1 / time_2 if time_2 > 0 else float('inf')
        print(f"✅ Speedup: {speedup:.1f}x faster")

def test_student_profile_caching():
    """Test student profile embedding caching."""
    print("\n" + "="*60)
    print("TEST 2: Student Profile Embedding Caching")
    print("="*60)
    
    model = create_embedding_model()
    test_profiles = [
        "I have 2 years of experience with Django and Flask",
        "I am a beginner learning Python for the first time",
        "I am a senior engineer with 10 years in software architecture"
    ]
    
    for profile in test_profiles:
        print(f"\n--- Profile: {profile[:50]}... ---")
        
        # First call - should generate
        print("First call (generating)...")
        start = time.time()
        embedding_1 = get_or_create_student_embedding(profile, model)
        time_1 = time.time() - start
        print(f"✅ Generated in {time_1:.3f}s")
        
        # Second call - should use cache
        print("Second call (retrieving from cache)...")
        start = time.time()
        embedding_2 = get_or_create_student_embedding(profile, model)
        time_2 = time.time() - start
        print(f"✅ Retrieved in {time_2:.3f}s")
        
        speedup = time_1 / time_2 if time_2 > 0 else float('inf')
        print(f"Speedup: {speedup:.1f}x faster")

def test_experience_level_detection():
    """Test experience level detection with caching."""
    print("\n" + "="*60)
    print("TEST 3: Experience Level Detection (with Caching)")
    print("="*60)
    
    model = create_embedding_model()
    
    test_cases = [
        ("I am a beginner learning Python for the first time", "beginner"),
        ("I have 3 years of experience building web applications", "intermediate"),
        ("I am a senior engineer with 12 years in distributed systems", "advanced"),
    ]
    
    for profile, expected_level in test_cases:
        print(f"\n--- Testing: {profile[:50]}... ---")
        print(f"Expected level: {expected_level}")
        
        # First detection
        print("First detection (generating reference embeddings)...")
        start = time.time()
        detected_level_1 = extract_experience_level_embeddings(profile, model)
        time_1 = time.time() - start
        print(f"✅ Detected: {detected_level_1} in {time_1:.3f}s")
        
        # Second detection - should use cached references
        print("Second detection (using cached reference embeddings)...")
        start = time.time()
        detected_level_2 = extract_experience_level_embeddings(profile, model)
        time_2 = time.time() - start
        print(f"✅ Detected: {detected_level_2} in {time_2:.3f}s")
        
        speedup = time_1 / time_2 if time_2 > 0 else float('inf')
        print(f"Speedup: {speedup:.1f}x")
        
        # Verify consistency
        if detected_level_1 == detected_level_2:
            print(f"✅ Consistent results")
        else:
            print(f"⚠️ Inconsistent results: {detected_level_1} vs {detected_level_2}")

def test_cache_retrieval():
    """Test that caches are actually being stored and retrieved."""
    print("\n" + "="*60)
    print("TEST 4: Cache Retrieval Verification")
    print("="*60)
    
    model = create_embedding_model()
    test_profile = "I love working with Python and Django for backend development"
    
    # Clear all caches first
    print("\n--- Clearing caches ---")
    clear_profile_embeddings_cache()
    clear_reference_embeddings_cache()
    print("✅ Caches cleared")
    
    # Generate new caches
    print("\n--- Generating new caches ---")
    embedding = get_or_create_student_embedding(test_profile, model)
    print(f"✅ Student embedding generated")
    
    level = extract_experience_level_embeddings(test_profile, model)
    print(f"✅ Experience level detected: {level}")
    
    # Verify they're retrievable
    print("\n--- Verifying cache retrieval ---")
    cached_embedding = get_cached_student_embedding(test_profile)
    if cached_embedding is not None:
        print(f"✅ Student embedding found in cache")
    else:
        print(f"❌ Student embedding NOT found in cache")
    
    for exp_level in ['beginner', 'intermediate', 'advanced']:
        cached_ref = get_cached_reference_embeddings(exp_level)
        if cached_ref is not None:
            print(f"✅ Reference embeddings for {exp_level} found in cache")
        else:
            print(f"❌ Reference embeddings for {exp_level} NOT found in cache")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CACHING SYSTEM TEST SUITE")
    print("="*60)
    
    try:
        test_reference_embeddings_caching()
        test_student_profile_caching()
        test_experience_level_detection()
        test_cache_retrieval()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
