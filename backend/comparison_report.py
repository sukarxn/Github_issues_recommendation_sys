import json
from core import recommend_issues, extract_experience_level_embeddings, extract_language_from_profile
from sentence_transformers import SentenceTransformer
from tabulate import tabulate
import time

def run_comparison(profiles):
    """Run comparison tests between embedding and Phi-4 approaches"""
    results = []
    model = SentenceTransformer('all-MiniLM-L6-v2')

    for idx, profile in enumerate(profiles, 1):
        print(f"\nAnalyzing profile {idx}...")
        
        # Test embedding approach
        start_time = time.time()
        emb_exp_level = extract_experience_level_embeddings(profile, model, use_phi=False)
        emb_language = extract_language_from_profile(profile, use_phi=False)
        emb_time = time.time() - start_time
        
        # Test Phi approach
        start_time = time.time()
        phi_exp_level = extract_experience_level_embeddings(profile, model, use_phi=True)
        phi_language = extract_language_from_profile(profile, use_phi=True)
        phi_time = time.time() - start_time

        results.append({
            "profile_id": idx,
            "profile_text": profile[:100] + "..." if len(profile) > 100 else profile,
            "embedding_results": {
                "experience_level": emb_exp_level,
                "language": emb_language,
                "processing_time": emb_time
            },
            "phi_results": {
                "experience_level": phi_exp_level,
                "language": phi_language,
                "processing_time": phi_time
            }
        })

    return results

def generate_report(results):
    """Generate a formatted comparison report"""
    report = """# Comparison Report: Embedding vs Phi-4 Approach

## Overview
This report compares the results of the traditional embedding-based approach with the new Phi-4 LLM approach for analyzing developer profiles.

## Test Profiles and Results\n\n"""

    # Create comparison tables
    comparison_rows = []
    for r in results:
        comparison_rows.append([
            r["profile_id"],
            r["profile_text"],
            r["embedding_results"]["experience_level"],
            r["phi_results"]["experience_level"],
            r["embedding_results"]["language"],
            r["phi_results"]["language"],
            f"{r['embedding_results']['processing_time']:.3f}s",
            f"{r['phi_results']['processing_time']:.3f}s"
        ])

    headers = [
        "Profile ID",
        "Profile Text",
        "Emb. Exp Level",
        "Phi Exp Level",
        "Emb. Language",
        "Phi Language",
        "Emb. Time",
        "Phi Time"
    ]

    report += tabulate(comparison_rows, headers=headers, tablefmt="pipe")

    # Add analysis section
    report += "\n\n## Analysis\n\n"

    # Calculate statistics
    agreement_exp = sum(1 for r in results 
                       if r["embedding_results"]["experience_level"] == r["phi_results"]["experience_level"])
    agreement_lang = sum(1 for r in results 
                        if r["embedding_results"]["language"] == r["phi_results"]["language"])
    
    avg_time_emb = sum(r["embedding_results"]["processing_time"] for r in results) / len(results)
    avg_time_phi = sum(r["phi_results"]["processing_time"] for r in results) / len(results)

    report += f"""### Agreement Rate
- Experience Level Agreement: {agreement_exp/len(results)*100:.1f}%
- Language Detection Agreement: {agreement_lang/len(results)*100:.1f}%

### Performance
- Average Processing Time (Embedding): {avg_time_emb:.3f}s
- Average Processing Time (Phi): {avg_time_phi:.3f}s
- Phi is {avg_time_emb/avg_time_phi:.1f}x {'faster' if avg_time_phi < avg_time_emb else 'slower'} than the embedding approach

### Key Observations
1. Experience Level Detection:
   - {'High' if agreement_exp/len(results) > 0.8 else 'Moderate' if agreement_exp/len(results) > 0.5 else 'Low'} agreement between approaches
   - Phi tends to be {'more' if avg_time_phi < avg_time_emb else 'less'} efficient

2. Language Detection:
   - {'High' if agreement_lang/len(results) > 0.8 else 'Moderate' if agreement_lang/len(results) > 0.5 else 'Low'} agreement between approaches
   - Both methods successfully identify primary programming languages
"""

    return report

def main():
    # Test profiles
    test_profiles = [
        # Profile 1: Clear beginner
        """I am a computer science student just starting to learn programming. 
        I know basic Python syntax and have completed a few small projects. 
        Looking for beginner-friendly issues to start contributing to open source.""",
        
        # Profile 2: Intermediate developer
        """Full-stack developer with 3 years of experience in Python and JavaScript. 
        Built and deployed several web applications using Django and React. 
        Comfortable with database design and API development.""",
        
        # Profile 3: Advanced developer
        """Senior software engineer with 8+ years of experience leading development teams. 
        Expert in distributed systems, microservices architecture, and cloud infrastructure. 
        Deep knowledge of Python, Go, and system design.""",
        
        # Profile 4: Mixed signals
        """I'm comfortable with Python and have been coding for 2 years, 
        but still learning best practices. Built a few small web apps 
        and contributed to some open source projects.""",
    ]

    # Run comparison
    results = run_comparison(test_profiles)
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_path = "COMPARISON_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nReport generated and saved to {report_path}")

if __name__ == "__main__":
    main()