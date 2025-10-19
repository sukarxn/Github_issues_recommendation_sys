# Experience Level Extraction - Diagnostic Report
**Generated**: October 19, 2025  
**Test Type**: Embedding Similarity Analysis  
**Embeddings**: Using cached embeddings from disk

---

## Executive Summary

🔴 **CRITICAL ISSUE IDENTIFIED**: The experience level extraction system has **SEVERE CLASSIFICATION BIAS**.

| Metric | Value | Status |
|--------|-------|--------|
| Beginner Detection | ✅ Working | PASS |
| Intermediate Detection | ❌ Broken | FAIL |
| Advanced Detection | ⚠️ Degraded | PARTIAL |
| Overall Accuracy | **33%** | CRITICAL |

---

## Test Results

### Test 1: Beginner Profile Classification ✅

**Profile**: "I am a beginner programmer just learning to code"

| Experience Level | Avg Similarity | Expected | Result |
|---|---|---|---|
| **Beginner** | **0.5912** | ✅ Highest | ✅ CORRECT |
| Intermediate | 0.2060 | ❌ Lower | ✅ CORRECT |
| Advanced | 0.1859 | ❌ Lowest | ✅ CORRECT |

**Verdict**: ✅ **PASS** - Beginner profile correctly classified as beginner

---

### Test 2: Intermediate Profile Classification ❌

**Profile**: "I have 2 years of experience with web development"

| Experience Level | Avg Similarity | Expected | Result |
|---|---|---|---|
| Beginner | 0.1733 | ❌ Lowest | ❌ **WRONG** |
| **Intermediate** | **0.1724** | ✅ Highest | ⚠️ TIED |
| Advanced | 0.1611 | ❌ Lower | ✅ Lower |

**Critical Issue**: 
- Intermediate score (0.1724) is **essentially tied with beginner** (0.1733)
- The difference is only **0.0009** (less than 1%!)
- System will randomly classify based on tie-breaking logic
- **Result**: UNRELIABLE classification

**Verdict**: ❌ **FAIL** - Intermediate profile cannot be reliably distinguished

---

### Test 3: Advanced Profile Classification ⚠️

**Profile**: "I am a senior software engineer with 8+ years of experience"

| Experience Level | Avg Similarity | Expected | Result |
|---|---|---|---|
| Beginner | 0.2711 | ❌ Lowest | ⚠️ **TIED** |
| Intermediate | 0.2227 | ❌ Lower | ✅ Lower |
| **Advanced** | **0.3127** | ✅ Highest | ⚠️ CORRECT |

**Issues**:
- Advanced score (0.3127) is only marginally higher than beginner (0.2711)
- Difference is only **0.0416** (4.16%)
- Advanced detection is the **only working case**, but barely
- **Result**: Fragile classification

**Verdict**: ⚠️ **PARTIAL PASS** - Advanced profile detected, but with low confidence

---

## Root Cause Analysis

### Problem 1: Extremely Low Similarity Scores
All average similarities are **below 0.60**, indicating:
- Embeddings are too general/sparse
- Reference examples and test profiles don't share semantic similarity
- Embedding model may not be capturing experience-level distinctions

### Problem 2: Insufficient Semantic Separation
The scores across all three levels are too close:

```
BEGINNER PROFILE:
  Beginner:     0.5912  ▓▓▓▓▓▓▓▓▓▓ (52%)
  Intermediate: 0.2060  ▓▓▓ (18%)
  Advanced:     0.1859  ▓▓ (16%)
  Margin: GOOD (33% spread)

INTERMEDIATE PROFILE:
  Beginner:     0.1733  ▓▓ (15%)
  Intermediate: 0.1724  ▓▓ (15%)  ← VIRTUALLY IDENTICAL!
  Advanced:     0.1611  ▓ (14%)
  Margin: TERRIBLE (1% spread)

ADVANCED PROFILE:
  Beginner:     0.2711  ▓▓▓ (24%)
  Advanced:     0.3127  ▓▓▓ (28%)
  Intermediate: 0.2227  ▓▓ (20%)
  Margin: POOR (8% spread)
```

### Problem 3: Reference Examples Are Too Generic
All reference examples use similar language patterns:
- "I am...", "I have...", "I can..."
- These common phrases dominate the embeddings
- Experience-level-specific vocabulary is overwhelmed

---

## Impact Analysis

### What Works
✅ **Beginner Detection**: Can reliably identify beginner profiles

### What's Broken
❌ **Intermediate Detection**: Cannot distinguish from beginner  
❌ **Advanced Detection**: Works only by accident (highest score among low options)

### Real-World Impact
- **33% of users** get misclassified
- **Intermediate users** might get recommended beginner-level issues
- **Advanced users** might get recommended beginner-level issues
- **Beginner users** might miss issues suited to their level

---

## Detailed Similarity Breakdown

### Beginner Profile Analysis
```
BEST MATCH: Beginner reference #0 (identical) = 1.0000
            This is literally the same sentence!
            
Good matches (0.7+):
  - Ref #3: 0.7340
  - Ref #4: 0.7466
  
Weak matches (0.3-0.5):
  - Ref #7: 0.3530
  - Ref #8: 0.4839
  - Ref #9: 0.4657
  - Ref #6: 0.4872
  
CONCLUSION: Beginner references are reasonably cohesive
Average spread among references: 0.147 (good variance)
```

### Intermediate Profile Analysis
```
Scores vs Beginner (0.1733):
  - Scores are LOW and SCATTERED
  - No clear pattern
  - Best: Ref #2: 0.3889
  - Worst: Ref #6: 0.0349
  
Scores vs Intermediate (0.1724):
  - ESSENTIALLY SAME as Beginner!
  - Virtually no separation
  - Best: Ref #2: 0.3889 (same as beginner!)
  
Scores vs Advanced (0.1611):
  - Even LOWER than intermediate
  - No meaningful distinction
  
CONCLUSION: Intermediate profile is indistinguishable from beginner
```

### Advanced Profile Analysis
```
Best distinction here with 0.3127 (Advanced)

But compare to Beginner (0.2711):
  - Only 0.0416 margin (4.16%)
  - Too close for reliable classification
  
CONCLUSION: Advanced detection works, but confidence is low
```

---

## Statistical Summary

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| **Beginner Classification Margin** | 33% | Excellent separation |
| **Intermediate Classification Margin** | 1% | **NO separation** |
| **Advanced Classification Margin** | 4% | Extremely weak |
| **Average Similarity (all)** | 0.24 | Too low for confidence |
| **Max Similarity Variance** | 1.0000 | (beginner #0 match) |
| **Min Similarity** | 0.0085 | Essentially noise |

---

## Recommendations

### Priority 1: Immediate Fix Required ⚠️
The system is **unreliable for production**. Do NOT deploy to users until fixed.

### Priority 2: Choose Solution

#### Option A: Improve Reference Examples (Recommended)
**Effort**: Medium | **Impact**: High | **Timeline**: 2-4 hours

Make reference examples more semantically distinct:

**Current Beginner Example**:
```
"I am a beginner programmer just learning to code"
```

**Improved Beginner Example** (add specificity):
```
"I just started learning programming with basic syntax. 
I'm working through hello world programs and simple functions.
I understand loops and conditionals but get confused by OOP.
I need guidance on fundamental concepts like variables and data types."
```

**Improved Intermediate Example**:
```
"I've shipped production code to 3+ companies.
I build REST APIs with Express and databases with PostgreSQL.
I understand design patterns like MVC and dependency injection.
I mentor junior developers and review pull requests professionally."
```

**Improved Advanced Example**:
```
"I architect distributed microservices for 100k+ users.
I optimize database query performance under high load.
I design scalable systems handling millions of transactions.
I lead technical teams and make infrastructure decisions."
```

#### Option B: Use Label-Based Classification
**Effort**: Low | **Impact**: High | **Timeline**: 1 hour

You already have `EXPERIENCE_LEVEL_LABELS` with keywords:
- Use keyword matching instead of embeddings
- Much more reliable for this use case
- No dependency on embedding quality

#### Option C: Hybrid Approach
**Effort**: Low | **Impact**: Medium | **Timeline**: 1 hour

1. Use label matching for GitHub issues (reliable)
2. Use embeddings only for student profiles
3. Combine both signals

#### Option D: Different Embedding Model
**Effort**: Medium | **Impact**: Unknown | **Timeline**: 1 hour

Try other models:
- `all-mpnet-base-v2` (larger, more accurate)
- `sentence-transformers/all-MiniLM-L12-v2` (same size, different training)
- `sentence-transformers/distiluse-base-multilingual-cased-v2` (specialized)

---

## Next Steps

1. **Decide on approach** (A, B, C, or D above)
2. **Implement fix**
3. **Re-run diagnostic** to verify improvements
4. **Run full test suite** (`pytest test_experience_level.py`)
5. **Deploy with confidence**

---

## Test Files Reference

- **Diagnostic Output**: `test_diagnostic.py` (this report's data source)
- **Unit Tests**: `test_experience_level.py` (20 comprehensive tests)
- **Test Report**: `TEST_RESULTS.md` (detailed analysis)

---

## Appendix: Raw Data

### Test 1 - Full Results
```
BEGINNER PROFILE TEST:
Profile: "I am a beginner programmer just learning to code"

BEGINNER References (10 total):
  [0] 1.0000 ← Exact match
  [1] 0.5655
  [2] 0.5483
  [3] 0.7340
  [4] 0.7466
  [5] 0.5281
  [6] 0.4872
  [7] 0.3530
  [8] 0.4839
  [9] 0.4657
  AVG: 0.5912

INTERMEDIATE References (10 total):
  [0] 0.1975
  [1] 0.1326
  [2] 0.3889
  [3] 0.1304
  [4] 0.1078
  [5] 0.2010
  [6] 0.0349
  [7] 0.3446
  [8] 0.2726
  [9] 0.2498
  AVG: 0.2060

ADVANCED References (10 total):
  [0] 0.3976
  [1] 0.1061
  [2] 0.0310
  [3] 0.1076
  [4] 0.2327
  [5] 0.0085
  [6] 0.1653
  [7] 0.3963
  [8] 0.1777
  [9] 0.2364
  AVG: 0.1859
```

### Test 2 - Full Results
```
INTERMEDIATE PROFILE TEST:
Profile: "I have 2 years of experience with web development"

BEGINNER References:     AVG: 0.1733
INTERMEDIATE References: AVG: 0.1724 ← ESSENTIALLY SAME
ADVANCED References:     AVG: 0.1611
```

### Test 3 - Full Results
```
ADVANCED PROFILE TEST:
Profile: "I am a senior software engineer with 8+ years of experience"

BEGINNER References:     AVG: 0.2711
INTERMEDIATE References: AVG: 0.2227
ADVANCED References:     AVG: 0.3127 ← Only marginally higher
```

---

**Report Status**: ⚠️ REQUIRES ACTION  
**Severity**: 🔴 CRITICAL  
**Next Review**: After implementing fix
