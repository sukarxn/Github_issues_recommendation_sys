import json
from core import recommend_issues, extract_experience_level_embeddings, extract_language_from_profile
from sentence_transformers import SentenceTransformer
import time
from typing import List, Dict, Tuple

def get_comparison_analysis(expected: str, emb_result: str, phi_result: str) -> str:
    """Generate analysis text for a comparison"""
    if emb_result == expected and phi_result == expected:
        return f"Both approaches correctly identified '{expected}'"
    elif emb_result == expected:
        return f"Embedding approach correctly identified '{expected}', while Phi-4 predicted '{phi_result}'"
    elif phi_result == expected:
        return f"Phi-4 approach correctly identified '{expected}', while Embedding predicted '{emb_result}'"
    else:
        return f"Neither approach correctly identified '{expected}' (Embedding: '{emb_result}', Phi-4: '{phi_result}')"

def get_performance_analysis(emb_time: float, phi_time: float) -> str:
    """Generate performance comparison text"""
    ratio = phi_time / emb_time
    if ratio > 1:
        return f"Embedding approach was {ratio:.1f}x faster"
    else:
        return f"Phi-4 approach was {1/ratio:.1f}x faster"

def generate_test_cases() -> List[Dict]:
    """Generate test cases with known ground truth"""
    return [
        {
            "profile": """I just started learning Python last month. I've completed some basic tutorials 
            and understand variables, loops, and functions. I'm looking for very simple issues to start 
            with as this would be my first open source contribution.""",
            "expected_level": "beginner",
            "expected_language": "python",
            "description": "Clear beginner with basic Python"
        },
        {
            "profile": """Mid-level software engineer with 3 years of professional Python experience. 
            I've built several Django applications, worked with databases, and have good understanding 
            of software architecture. I contribute regularly to open source projects.""",
            "expected_level": "intermediate",
            "expected_language": "python",
            "description": "Intermediate Python developer"
        },
        {
            "profile": """Tech lead with 8+ years of experience in building large-scale distributed systems. 
            Expert in Python and Go, with deep knowledge of system design and performance optimization. 
            I mentor other developers and have architected several successful products.""",
            "expected_level": "advanced",
            "expected_language": "python",
            "description": "Senior Python developer"
        },
        {
            "profile": """JavaScript developer learning React. I've been coding for about 6 months and 
            have built a few small web applications. Looking for beginner-friendly frontend issues.""",
            "expected_level": "beginner",
            "expected_language": "javascript",
            "description": "Beginner JavaScript developer"
        },
        {
            "profile": """Full-stack developer with strong TypeScript and Node.js experience. 3 years of 
            professional experience building React applications. Familiar with modern web development 
            practices and tools.""",
            "expected_level": "intermediate",
            "expected_language": "javascript",
            "description": "Intermediate JavaScript/TypeScript developer"
        },
        {
            "profile": """Ruby on Rails expert with 5 years of experience. Built and maintained several 
            production applications, comfortable with database optimization and API design. Looking for 
            challenging backend issues.""",
            "expected_level": "advanced",
            "expected_language": "ruby",
            "description": "Advanced Ruby developer"
        },
        {
            "profile": """Started learning Java in my CS course this semester. Understanding OOP concepts 
            and basic data structures. Would like to contribute to beginner-level Java projects.""",
            "expected_level": "beginner",
            "expected_language": "java",
            "description": "Beginner Java student"
        },
        {
            "profile": """Golang developer with 2 years of experience in microservices and API development. 
            Good understanding of concurrency patterns and performance optimization. Regular contributor 
            to open source projects.""",
            "expected_level": "intermediate",
            "expected_language": "go",
            "description": "Intermediate Go developer"
        }
    ]

def run_accuracy_test(test_cases: List[Dict]) -> Dict:
    """Run accuracy tests for both approaches"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    results = {
        "embedding": {"correct_level": 0, "correct_lang": 0, "total_time": 0},
        "phi": {"correct_level": 0, "correct_lang": 0, "total_time": 0},
        "detailed_results": []
    }
    
    for case in test_cases:
        # Test embedding approach
        start_time = time.time()
        emb_level = extract_experience_level_embeddings(case["profile"], model, use_phi=False)
        emb_lang = extract_language_from_profile(case["profile"], use_phi=False)
        emb_time = time.time() - start_time
        
        # Test Phi approach
        start_time = time.time()
        phi_level = extract_experience_level_embeddings(case["profile"], model, use_phi=True)
        phi_lang = extract_language_from_profile(case["profile"], use_phi=True)
        phi_time = time.time() - start_time
        
        # Record results
        results["embedding"]["correct_level"] += (emb_level == case["expected_level"])
        results["embedding"]["correct_lang"] += (emb_lang == case["expected_language"])
        results["embedding"]["total_time"] += emb_time
        
        results["phi"]["correct_level"] += (phi_level == case["expected_level"])
        results["phi"]["correct_lang"] += (phi_lang == case["expected_language"])
        results["phi"]["total_time"] += phi_time
        
        results["detailed_results"].append({
            "description": case["description"],
            "expected": {
                "level": case["expected_level"],
                "language": case["expected_language"],
                "profile": case["profile"]
            },
            "embedding_results": {
                "level": emb_level,
                "language": emb_lang,
                "time": emb_time
            },
            "phi_results": {
                "level": phi_level,
                "language": phi_lang,
                "time": phi_time
            }
        })
    
    return results

def generate_accuracy_report(results: Dict) -> str:
    """Generate a detailed accuracy report"""
    total_cases = len(results["detailed_results"])
    
    report = """# Enhanced Comparison Report: Embedding vs Phi-4 Approach

## Test Cases Analysis

The following test cases were used to evaluate both approaches:
"""
    # Add detailed test case analysis
    for idx, case in enumerate(results["detailed_results"], 1):
        emb_level_correct = case['embedding_results']['level'] == case['expected']['level']
        emb_lang_correct = case['embedding_results']['language'] == case['expected']['language']
        phi_level_correct = case['phi_results']['level'] == case['expected']['level']
        phi_lang_correct = case['phi_results']['language'] == case['expected']['language']
        
        report += f"""
### Test Case {idx}: {case['description']}

**Profile Text:**
```
{case['expected']['profile']}
```

**Results:**
| Aspect | Expected | Embedding Approach | Phi-4 Approach |
|--------|----------|-------------------|----------------|
| Experience Level | {case['expected']['level']} | {case['embedding_results']['level']} {'✅' if emb_level_correct else '❌'} | {case['phi_results']['level']} {'✅' if phi_level_correct else '❌'} |
| Programming Language | {case['expected']['language']} | {case['embedding_results']['language']} {'✅' if emb_lang_correct else '❌'} | {case['phi_results']['language']} {'✅' if phi_lang_correct else '❌'} |
| Processing Time | - | {case['embedding_results']['time']:.3f}s | {case['phi_results']['time']:.3f}s |

**Analysis:**
- Experience Level: {get_comparison_analysis(case['expected']['level'], case['embedding_results']['level'], case['phi_results']['level'])}
- Language Detection: {get_comparison_analysis(case['expected']['language'], case['embedding_results']['language'], case['phi_results']['language'])}
- Performance: {get_performance_analysis(case['embedding_results']['time'], case['phi_results']['time'])}
"""

    report += """
## Overall Accuracy Analysis

### Overall Accuracy

#### Embedding Approach:
- Experience Level Accuracy: {:.1f}%
- Language Detection Accuracy: {:.1f}%
- Average Processing Time: {:.3f}s per profile

#### Phi-4 Approach:
- Experience Level Accuracy: {:.1f}%
- Language Detection Accuracy: {:.1f}%
- Average Processing Time: {:.3f}s per profile

### Detailed Results

| Case | Expected | Embedding Results | Phi Results |
|------|----------|------------------|-------------|
""".format(
        results["embedding"]["correct_level"] / total_cases * 100,
        results["embedding"]["correct_lang"] / total_cases * 100,
        results["embedding"]["total_time"] / total_cases,
        results["phi"]["correct_level"] / total_cases * 100,
        results["phi"]["correct_lang"] / total_cases * 100,
        results["phi"]["total_time"] / total_cases
    )

    for case in results["detailed_results"]:
        report += f"""| {case['description']} | Level: {case['expected']['level']}<br>Lang: {case['expected']['language']} | Level: {case['embedding_results']['level']}<br>Lang: {case['embedding_results']['language']}<br>Time: {case['embedding_results']['time']:.3f}s | Level: {case['phi_results']['level']}<br>Lang: {case['phi_results']['language']}<br>Time: {case['phi_results']['time']:.3f}s |
"""

    # Add analysis
    report += """
## Key Findings

1. Experience Level Detection:
"""
    if results["embedding"]["correct_level"] > results["phi"]["correct_level"]:
        report += "   - Embedding approach shows higher accuracy in experience level detection\n"
    elif results["embedding"]["correct_level"] < results["phi"]["correct_level"]:
        report += "   - Phi-4 approach shows higher accuracy in experience level detection\n"
    else:
        report += "   - Both approaches show equal accuracy in experience level detection\n"

    report += """
2. Language Detection:
"""
    if results["embedding"]["correct_lang"] > results["phi"]["correct_lang"]:
        report += "   - Embedding approach shows higher accuracy in language detection\n"
    elif results["embedding"]["correct_lang"] < results["phi"]["correct_lang"]:
        report += "   - Phi-4 approach shows higher accuracy in language detection\n"
    else:
        report += "   - Both approaches show equal accuracy in language detection\n"

    report += """
3. Performance Comparison:
   - Average time per profile (Embedding): {:.3f}s
   - Average time per profile (Phi-4): {:.3f}s
   - Speed difference: Phi-4 is {:.1f}x {} than Embedding approach
""".format(
        results["embedding"]["total_time"] / total_cases,
        results["phi"]["total_time"] / total_cases,
        abs(results["embedding"]["total_time"] / results["phi"]["total_time"]),
        "faster" if results["phi"]["total_time"] < results["embedding"]["total_time"] else "slower"
    )

    return report

def main():
    # Generate and run test cases
    test_cases = generate_test_cases()
    results = run_accuracy_test(test_cases)
    
    # Generate and save report
    report = generate_accuracy_report(results)
    report_path = "ACCURACY_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nAccuracy report generated and saved to {report_path}")

if __name__ == "__main__":
    main()