 
import argparse
import sys
import os
from core import recommend_issues

def print_issues(issues, ranked: bool = False):
    if not issues:
        print("No issues found.")
        return
    if ranked:
        for idx, issue in enumerate(issues, start=1):
            title = issue.get("title", "").strip()
            url = issue.get("url", "").strip()
            repo = issue.get("repo", "").strip()
            score = issue.get("similarity", None)
            print(f"{idx}. [{repo}] {title} (similarity: {score:.4f})\n   {url}")
    else:
        for idx, issue in enumerate(issues, start=1):
            title = issue.get("title", "").strip()
            url = issue.get("url", "").strip()
            repo = issue.get("repo", "").strip()
            print(f"{idx}. [{repo}] {title}\n   {url}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and print GitHub 'good first issue' issues from top repositories.")
    parser.add_argument("--language", "-l", default="all", help="Programming language to filter repositories by (default: all; use a language name to filter)")
    parser.add_argument("--per-page", "-n", type=int, default=20, help="Total number of issues to print (default: 20)")
    parser.add_argument("--top-n", type=int, default=100, help="Number of top repositories by stars to search (default: 100)")
    parser.add_argument("--student-profile", "-p", type=str, help="Student profile text or path to a text file containing the profile")
    parser.add_argument("--model", "-m", type=str, default="all-MiniLM-L6-v2", help="SentenceTransformer model name (default: all-MiniLM-L6-v2)")
    args = parser.parse_args()

    profile_text = args.student_profile
    if profile_text and os.path.isfile(profile_text):
        with open(profile_text, 'r', encoding='utf-8') as f:
            profile_text = f.read().strip()

    try:
        issues = recommend_issues(
            language=args.language,
            per_page=args.per_page,
            top_n=args.top_n,
            student_profile=profile_text,
            model_name=args.model,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print_issues(issues, ranked=bool(profile_text))

if __name__ == "__main__":
    main()