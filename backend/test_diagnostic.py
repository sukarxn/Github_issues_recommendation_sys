"""
Diagnostic test to understand why experience level extraction is biased to beginner.
"""

from sentence_transformers import SentenceTransformer, util
import numpy as np
from core import (
    EXPERIENCE_LEVEL_REFERENCES,
    get_or_create_reference_embeddings,
    get_or_create_student_embedding
)

model = SentenceTransformer('all-MiniLM-L6-v2')

# Test 1: Check what happens with beginner profile
print("=" * 80)
print("TEST 1: Beginner Profile from References")
print("=" * 80)

beginner_profile = EXPERIENCE_LEVEL_REFERENCES['beginner'][0]
print(f"Profile: {beginner_profile}\n")

student_embedding = get_or_create_student_embedding(beginner_profile, model)
print(f"Student embedding type: {type(student_embedding)}")
print(f"Student embedding shape: {student_embedding.shape if hasattr(student_embedding, 'shape') else 'N/A'}\n")

# Test similarity with each level
for level in ['beginner', 'intermediate', 'advanced']:
    ref_embeddings = get_or_create_reference_embeddings(level, EXPERIENCE_LEVEL_REFERENCES[level], model)
    
    level_scores = []
    for i, ref_embedding in enumerate(ref_embeddings):
        try:
            # Try the comparison
            print(f"  Ref embedding {i} type: {type(ref_embedding)}")
            
            # Convert to tensors if needed
            if not hasattr(student_embedding, 'device'):  # It's numpy
                import torch
                student_tensor = torch.from_numpy(student_embedding).float()
            else:
                student_tensor = student_embedding
            
            similarity = util.pytorch_cos_sim(student_tensor, ref_embedding)
            score = similarity.item()
            level_scores.append(score)
            print(f"    Similarity: {score:.4f}")
        except Exception as e:
            print(f"    Error: {e}")
    
    avg_score = np.mean(level_scores) if level_scores else 0
    print(f"  {level.upper()}: Average Similarity = {avg_score:.4f}\n")

# Test 2: Check intermediate profile
print("=" * 80)
print("TEST 2: Intermediate Profile from References")
print("=" * 80)

intermediate_profile = EXPERIENCE_LEVEL_REFERENCES['intermediate'][0]
print(f"Profile: {intermediate_profile}\n")

student_embedding = get_or_create_student_embedding(intermediate_profile, model)

for level in ['beginner', 'intermediate', 'advanced']:
    ref_embeddings = get_or_create_reference_embeddings(level, EXPERIENCE_LEVEL_REFERENCES[level], model)
    
    level_scores = []
    for ref_embedding in ref_embeddings:
        try:
            if not hasattr(student_embedding, 'device'):
                import torch
                student_tensor = torch.from_numpy(student_embedding).float()
            else:
                student_tensor = student_embedding
            
            similarity = util.pytorch_cos_sim(student_tensor, ref_embedding)
            level_scores.append(similarity.item())
        except Exception as e:
            pass
    
    avg_score = np.mean(level_scores) if level_scores else 0
    print(f"  {level.upper()}: Average Similarity = {avg_score:.4f}\n")

# Test 3: Check advanced profile
print("=" * 80)
print("TEST 3: Advanced Profile from References")
print("=" * 80)

advanced_profile = EXPERIENCE_LEVEL_REFERENCES['advanced'][0]
print(f"Profile: {advanced_profile}\n")

student_embedding = get_or_create_student_embedding(advanced_profile, model)

for level in ['beginner', 'intermediate', 'advanced']:
    ref_embeddings = get_or_create_reference_embeddings(level, EXPERIENCE_LEVEL_REFERENCES[level], model)
    
    level_scores = []
    for ref_embedding in ref_embeddings:
        try:
            if not hasattr(student_embedding, 'device'):
                import torch
                student_tensor = torch.from_numpy(student_embedding).float()
            else:
                student_tensor = student_embedding
            
            similarity = util.pytorch_cos_sim(student_tensor, ref_embedding)
            level_scores.append(similarity.item())
        except Exception as e:
            pass
    
    avg_score = np.mean(level_scores) if level_scores else 0
    print(f"  {level.upper()}: Average Similarity = {avg_score:.4f}\n")
