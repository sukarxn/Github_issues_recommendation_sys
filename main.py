import requests
from typing import List, Dict, Tuple, Optional
import argparse
import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _auth_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-issues-reco/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_top_repositories(language: str | None, top_n: int = 100) -> List[Tuple[str, str, int]]:
    """Fetch top repositories by stars.

    Returns list of (owner, repo, stargazers_count)
    """
    url = "https://api.github.com/search/repositories"
    token = os.getenv("GITHUB_TOKEN")
    headers = _auth_headers()

    q = "stars:>0"
    if language:
        q += f" language:{language}"

    params = {
        "q": q,
        "per_page": max(1, min(int(top_n), 100)),
        "sort": "stars",
        "order": "desc",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    repos: List[Tuple[str, str, int]] = []
    for it in items:
        full = it.get("full_name", "")  # owner/repo
        if "/" not in full:
            continue
        owner, repo = full.split("/", 1)
        repos.append((owner, repo, int(it.get("stargazers_count", 0))))
    return repos


def fetch_repo_good_first_issues(owner: str, repo: str, limit: int) -> List[Dict]:
    """Fetch 'good first issue' issues from a specific repo.

    Excludes pull requests.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = _auth_headers()
    params = {
        "state": "open",
        "sort": "updated",
        "direction": "desc",
        "per_page": max(1, min(int(limit), 100)),
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    issues = []
    wanted = {"good first issue", "good-first-issue"}
    for item in r.json():
        # Skip pull requests
        if "pull_request" in item:
            continue
        labels = {str(l.get("name", "")).strip().casefold() for l in item.get("labels", [])}
        if labels & wanted:
            issues.append(
                {
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "url": item.get("html_url", ""),
                    "repo": f"{owner}/{repo}",
                }
            )
            if len(issues) >= limit:
                break
    return issues


def fetch_github_issues(language: str = "typescript", per_page: int = 20, top_n: int = 100) -> List[Dict]:
    """Fetch open 'good first issue' issues from the most popular repositories.

    Args:
        language: Programming language to filter repositories by (None for all languages).
        per_page: Total number of issues to return overall.
        top_n: Number of top repositories by stars to consider (max 100 due to API per_page).
    """
    token = os.getenv("GITHUB_TOKEN")
    # If unauthenticated, keep calls within the 60/hour limit: 1 (search repos) + top_n (repo issues)
    if not token:
        orig = top_n
        top_n = min(top_n, 30)
        if orig > top_n:
            print(
                f"Warning: No GITHUB_TOKEN detected; limiting repositories to {top_n} to avoid rate limits.",
                file=sys.stderr,
            )

    repos = fetch_top_repositories(language or None, top_n=min(100, top_n))
    remaining = max(1, int(per_page))
    all_issues: List[Dict] = []
    for owner, repo, _stars in repos:
        batch = fetch_repo_good_first_issues(owner, repo, limit=min(remaining, 100))
        if batch:
            all_issues.extend(batch)
            remaining = per_page - len(all_issues)
            if remaining <= 0:
                break
    return all_issues[:per_page]


def create_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """Load and return the sentence transformer model."""
    return SentenceTransformer(model_name)


def generate_issue_embeddings(issues: List[Dict], model: SentenceTransformer) -> np.ndarray:
    """Generate embeddings for a list of issues.
    
    Args:
        issues: List of issue dictionaries with 'title' and 'body' keys.
        model: SentenceTransformer model to use for encoding.
    
    Returns:
        numpy array of shape (num_issues, embedding_dim)
    """
    if not issues:
        return np.array([])
    
    # Combine title and body for each issue
    texts = [
        f"{issue.get('title', '').strip()} {issue.get('body', '').strip()}"
        for issue in issues
    ]
    return model.encode(texts, show_progress_bar=False)


def generate_student_profile_embedding(profile_text: str, model: SentenceTransformer) -> np.ndarray:
    """Generate embedding for a student profile.
    
    Args:
        profile_text: Text describing the student's skills, interests, and background.
        model: SentenceTransformer model to use for encoding.
    
    Returns:
        numpy array of shape (embedding_dim,)
    """
    return model.encode(profile_text, show_progress_bar=False)


def compute_similarities(student_embedding: np.ndarray, issue_embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between student profile and each issue.
    
    Args:
        student_embedding: 1D array of student profile embedding.
        issue_embeddings: 2D array of issue embeddings (num_issues, embedding_dim).
    
    Returns:
        1D array of similarity scores for each issue.
    """
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([student_embedding], issue_embeddings)[0]


def rank_issues_by_similarity(
    issues: List[Dict], 
    student_embedding: np.ndarray, 
    issue_embeddings: np.ndarray
) -> List[Tuple[Dict, float]]:
    """Rank issues by similarity to student profile.
    
    Returns:
        List of (issue, similarity_score) tuples, sorted by descending similarity.
    """
    similarities = compute_similarities(student_embedding, issue_embeddings)
    ranked = list(zip(issues, similarities))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def print_issues(issues: List[Dict], ranked: bool = False):
    """Print issues to the terminal.
    
    Args:
        issues: List of issues (or list of (issue, score) tuples if ranked).
        ranked: If True, expects list of (issue, score) tuples.
    """
    if not issues:
        print("No issues found.")
        return
    
    if ranked:
        for idx, (issue, score) in enumerate(issues, start=1):
            title = issue.get("title", "").strip()
            url = issue.get("url", "").strip()
            repo = issue.get("repo", "").strip()
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

    try:
        lang = None if args.language.lower() in {"all", "*", ""} else args.language
        issues = fetch_github_issues(language=lang or "", per_page=args.per_page, top_n=args.top_n)
    except requests.RequestException as e:
        print(f"Network error while fetching issues: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # If student profile is provided, compute embeddings and rank issues
    if args.student_profile:
        print("Loading embedding model...", file=sys.stderr)
        model = create_embedding_model(args.model)
        
        # Load student profile (from file or direct text)
        profile_text = args.student_profile
        if os.path.isfile(args.student_profile):
            with open(args.student_profile, 'r', encoding='utf-8') as f:
                profile_text = f.read().strip()
        
        if not profile_text:
            print("Error: Student profile is empty.", file=sys.stderr)
            sys.exit(1)
        
        print("Generating embeddings...", file=sys.stderr)
        issue_embeddings = generate_issue_embeddings(issues, model)
        student_embedding = generate_student_profile_embedding(profile_text, model)
        
        print("Ranking issues by similarity...\n", file=sys.stderr)
        ranked_issues = rank_issues_by_similarity(issues, student_embedding, issue_embeddings)
        print_issues(ranked_issues, ranked=True)
    else:
        print_issues(issues, ranked=False)


if __name__ == "__main__":
    main()