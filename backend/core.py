import requests
from typing import List, Dict, Tuple, Optional
import os
import time
import json
import hashlib
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import diskcache as dc
from phi_predictor import predict_experience_level as phi_predict_experience
from phi_predictor import predict_programming_language as phi_predict_language

load_dotenv()

# Initialize disk cache
cache = dc.Cache('/tmp/github_issues_cache')
CACHE_TTL = 3600  # 1 hour in seconds


EXPERIENCE_LEVEL_REFERENCES = {
    'beginner': [
        "just started learning to code with basic syntax",
        "new to programming and learning fundamentals",
        "learning Python and understanding variables and loops",
        "basic knowledge of functions and simple data types",
        "student just starting my first programming course",
        "finished my first coding bootcamp and need practice",
        "been coding for only a few months",
        "understand basic syntax but struggle with complex logic",
        "enjoy solving simple algorithmic problems",
        "want beginner-friendly issues to learn from real projects",
    ],
    'intermediate': [
        # Production experience
        "shipped production code",
        "deployed applications to servers",
        "managed live systems",
        "fixed production bugs",
        "maintained deployed apps",
        "scaled applications",
        
        # APIs & Databases
        "build REST APIs",
        "created multiple endpoints",
        "queried databases efficiently",
        "optimized SQL queries",
        "worked with ORMs",
        "handled database migrations",
        "designed API schemas",
        "implemented caching layers",
        
        # Testing & Quality
        "wrote unit tests",
        "created integration tests",
        "achieved code coverage",
        "automated testing workflows",
        "used testing frameworks",
        "debugged complex issues",
        "fixed race conditions",
        "tested edge cases",
        
        # Code & Architecture
        "refactored legacy code",
        "applied design patterns",
        "used SOLID principles",
        "implemented MVC architecture",
        "separated concerns properly",
        "modularized code effectively",
        "documented code well",
        "reviewed pull requests",
        
        # Development Practices
        "used version control daily",
        "handled merge conflicts",
        "created meaningful commits",
        "maintained feature branches",
        "collaborated in teams",
        "communicated with developers",
        "followed coding standards",
        "met project deadlines",
        
        # Web Development
        "built full-stack features",
        "created responsive designs",
        "optimized frontend performance",
        "handled state management",
        "worked with frameworks",
        "integrated APIs",
        "improved user experience",
        
        # Data & Performance
        "optimized query performance",
        "debugged memory leaks",
        "profiled code bottlenecks",
        "improved load times",
        "reduced database calls",
        "implemented indexing strategies",
        "cached frequently used data",
        
        # DevOps & Tools
        "configured deployment pipelines",
        "automated build processes",
        "monitored application health",
        "handled error logging",
        "set up monitoring alerts",
        "managed configurations",
        "used containerization",
        
        # Problem Solving
        "solved real-world problems",
        "debugged production issues",
        "researched technical solutions",
        "experimented with new tools",
        "learned from code reviews",
        "improved existing systems",
        "identified performance issues",
    ],
    'advanced': [
        "architect distributed microservices handling millions of transactions",
        "lead engineering teams and make critical infrastructure decisions",
        "optimize performance for high-traffic systems and handle scale",
        "design and implement distributed systems with consensus algorithms",
        "expert in system architecture and technical strategy",
        "build microservices with message queues and event-driven architecture",
        "manage Kubernetes clusters and DevOps infrastructure at enterprise scale",
        "mentor senior developers and conduct architectural reviews",
        "maintain core libraries and frameworks used by thousands",
        "solve complex algorithmic problems and understand advanced data structures",
    ],
}

# Map experience levels to GitHub issue labels
EXPERIENCE_LEVEL_LABELS = {
    'beginner': [
        # Common beginner-friendly labels
        'good first issue',
        'good-first-issue',
        'beginner-friendly',
        'beginner',
        'starter',
        'easy',
        'easy-fix',
        'getting-started',
        'junior',
        'newbie',
        'entry-level',
        'first-timers-only',
        'low-hanging-fruit',
        'simple',
        'bite-sized',
        'documentation',
        'help-wanted',
        'newcomer',
        'student-friendly',
        'learning',
    ],
    'intermediate': [
        # Intermediate-level labels
        'intermediate',
        'medium',
        'medium-difficulty',
        'help wanted',
        'help-wanted',
        'bug',
        'feature-request',
        'feature',
        'enhancement',
        'improvement',
        'optimization',
        'refactor',
        'test',
        'testing',
        'unit-test',
        'integration-test',
        'ci/cd',
        'documentation-needed',
        'code-review',
        'type: bug',
        'type: feature',
        'priority: medium',
    ],
    'advanced': [
        # Advanced/complex labels
        'advanced',
        'hard',
        'complex',
        'difficult',
        'challenging',
        'performance',
        'performance-optimization',
        'architecture',
        'design',
        'refactor-major',
        'scalability',
        'concurrency',
        'security',
        'infrastructure',
        'devops',
        'critical',
        'priority: high',
        'priority: critical',
        'breaking-change',
        'senior',
        'expert-level',
        'deep-knowledge',
        'system-design',
        'large-refactor',
        'type: performance',
        'type: architecture',
    ],
}

def extract_experience_level_embeddings(profile_text: str, model: SentenceTransformer, use_phi: bool = False) -> str:
    """
    Extract experience level from student profile.
    Args:
        profile_text: The user's profile text
        model: The SentenceTransformer model (used if use_phi is False)
        use_phi: If True, use the Phi predictor instead of embeddings
    Returns:
        Experience level as string ('beginner', 'intermediate', 'advanced', or 'any')
    """
    if use_phi:
        return phi_predict_experience(profile_text)
    if not profile_text: 
        return "any"
    
    try:
        import torch
        
        # Get or generate cached student profile embedding
        student_embedding = get_or_create_student_embedding(profile_text, model)
        
        # Convert student embedding to tensor if needed and move to CPU
        if isinstance(student_embedding, np.ndarray):
            student_embedding = torch.from_numpy(student_embedding).float().cpu()
        else:
            student_embedding = student_embedding.cpu()
        
        # Find the best matching experience level
        best_level = 'any'
        best_score = -1
        
        for level, references in EXPERIENCE_LEVEL_REFERENCES.items():
            # Get cached or create reference embeddings for this level
            ref_embeddings = get_or_create_reference_embeddings(level, references, model)
            
            # Average similarity across all reference examples
            level_scores = []
            for ref_embedding in ref_embeddings:
                # Ensure both embeddings are on the same device (CPU)
                ref_embedding = ref_embedding.cpu() if hasattr(ref_embedding, 'cpu') else ref_embedding
                similarity = util.pytorch_cos_sim(student_embedding, ref_embedding)
                level_scores.append(similarity.item())
            
            avg_similarity = np.mean(level_scores)
            
            if avg_similarity > best_score:
                best_score = avg_similarity
                best_level = level
        
        print(f"✅ Detected experience level: {best_level} (similarity score: {best_score:.4f})")
        return best_level
    
    except Exception as e:
        print(f"⚠️ Error in experience level extraction: {e}")
        return "any"  # ← Safer fallback: no filtering


def _auth_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-issues-reco/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def extract_language_from_profile(profile_text: str, use_phi: bool = False) -> str:
    """
    Extract programming language from student profile.
    Args:
        profile_text: The user's profile text
        use_phi: If True, use the Phi predictor instead of keyword matching
    Returns:
        Programming language as string
    """
    if use_phi:
        return phi_predict_language(profile_text)
    if not profile_text:
        return "all"
    
    profile_text = profile_text.lower()

    #Define a list of popular programming languages
    languages = {
        'python': ['python', 'django', 'flask', 'fastapi', 'pytorch', 'tensorflow', 'pandas', 'numpy'],
        'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'node.js', 'nodejs', 'express'],
        'typescript': ['typescript', 'ts'],
        'java': ['java', 'spring', 'spring boot', 'maven', 'gradle'],
        'go': ['golang', 'go'],
        'rust': ['rust'],
        'ruby': ['ruby', 'rails', 'ruby on rails'],
        'php': ['php', 'laravel', 'symfony'],
        'c++': ['c++', 'cpp'],
        'csharp': ['c#', 'csharp', '.net', 'dotnet', 'asp.net'],
        'swift': ['swift', 'ios', 'swiftui'],
        'kotlin': ['kotlin', 'android'],
    }

    # Count occurrences of each language keyword in the profile text
    scores = {}
    for lang, keywords in languages.items():
        scores[lang] = sum(1 for kw in keywords if kw in profile_text)

    # Store the language with the highest score
    max_score = max(scores.values())
    
    # If no language keywords are found, return "all"
    if max_score == 0:
        return "all"
    # Return the language with the highest score
    return max(scores, key=scores.get)


def fetch_top_repositories(language: Optional[str], top_n: int = 100) -> List[Tuple[str, str, int]]:
    url = "https://api.github.com/search/repositories"
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
        full = it.get("full_name", "")
        if "/" not in full:
            continue
        owner, repo = full.split("/", 1)
        repos.append((owner, repo, int(it.get("stargazers_count", 0))))
    return repos

def fetch_repo_good_first_issues(
        owner: str,
        repo: str, 
        limit: int, 
        experience_level: str
    ) -> List[Dict]:
    """Fetch issues filtered by experience level labels."""
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

    # Special handling for "any" - fetch all issues without label filtering
    if experience_level == "any":
        wanted = None  # No filtering applied
    else:
        wanted = set(EXPERIENCE_LEVEL_LABELS.get(experience_level, []))

    for item in r.json():
        if "pull_request" in item:
            continue
        
        # If wanted is None, accept all issues (no label filtering for "any")
        if wanted is None:
            issues.append({
                "title": item.get("title", ""),
                "body": item.get("body", ""),
                "url": item.get("html_url", ""),
                "repo": f"{owner}/{repo}",
            })
        else:
            # Otherwise, check label intersection for specific experience levels
            labels = {str(l.get("name", "")).strip().casefold() for l in item.get("labels", [])}
            if labels & wanted:
                issues.append({
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "url": item.get("html_url", ""),
                    "repo": f"{owner}/{repo}",
                })
        
        if len(issues) >= limit:
            break
    return issues

def fetch_github_issues(
        language: str = "all", 
        per_page: int = 20, 
        top_n: int = 100,
        experience_level: str = "any"
    ) -> List[Dict]:
    """Fetch GitHub issues with caching."""
    
    # Check cache first
    cached_issues = get_cached_issues(language, top_n)
    if cached_issues is not None:
        return cached_issues
    
    # Fetch fresh issues from GitHub
    print(f"🔄 Fetching fresh issues for language: {language}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        orig = top_n
        top_n = min(top_n, 30)
        print(f"⚠️ No GITHUB_TOKEN set, limiting top_n from {orig} to {top_n}")

    repos = fetch_top_repositories(language or None, top_n=min(100, top_n))
    remaining = max(1, int(per_page))
    all_issues: List[Dict] = []

    for owner, repo, _stars in repos:
        batch = fetch_repo_good_first_issues(owner, repo, limit=min(remaining, 100), experience_level=experience_level)
        if batch:
            all_issues.extend(batch)
            remaining = per_page - len(all_issues)
            if remaining <= 0:
                break
    
    issues = all_issues[:per_page]
    
    # Cache the results
    set_cached_issues(language, top_n, issues)
    
    return issues

def create_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """
    Create a SentenceTransformer model for generating embeddings.
    Supported models:
    - 'all-MiniLM-L6-v2': Default, English-focused model
    - 'intfloat/multilingual-e5-base': Multilingual model supporting 100+ languages
    """
    return SentenceTransformer(model_name)

def generate_issue_embeddings(issues: List[Dict], model: SentenceTransformer) -> np.ndarray:
    if not issues:
        return np.array([])
    texts = [
        f"{issue.get('title', '').strip()} {issue.get('body', '').strip()}"
        for issue in issues
    ]
    return model.encode(texts, show_progress_bar=False)

def _get_profile_cache_key(profile_text: str) -> str:
    """Generate a unique cache key for profile text using hash."""
    profile_hash = hashlib.sha256(profile_text.encode()).hexdigest()
    return f"profile_embedding_{profile_hash}"

def _get_reference_embeddings_cache_key(level: str, model_name: str = 'all-MiniLM-L6-v2') -> str:
    """Generate a unique cache key for reference embeddings."""
    return f"reference_embeddings_{level}_{model_name}"

def _get_reference_embeddings_file_path() -> str:
    """Get the file path for storing reference embeddings."""
    cache_dir = '/tmp/github_issues_cache'
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, 'reference_embeddings.pkl')

def get_cached_reference_embeddings(level: str, model_name: str = 'all-MiniLM-L6-v2') -> Optional[List[np.ndarray]]:
    """Retrieve cached reference embeddings from disk."""
    try:
        file_path = _get_reference_embeddings_file_path()
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'rb') as f:
            embeddings_dict = pickle.load(f)
        
        cache_key = _get_reference_embeddings_cache_key(level, model_name)
        if cache_key in embeddings_dict:
            print(f"✅ Using cached reference embeddings for level: {level}")
            return embeddings_dict[cache_key]
        
    except Exception as e:
        print(f"⚠️ Error retrieving cached reference embeddings: {e}")
    
    return None

def set_cached_reference_embeddings(level: str, embeddings: List, model_name: str = 'all-MiniLM-L6-v2') -> None:
    """Cache reference embeddings to disk."""
    try:
        file_path = _get_reference_embeddings_file_path()
        
        # Load existing embeddings or create new dict
        embeddings_dict = {}
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                embeddings_dict = pickle.load(f)
        
        # Convert embeddings to numpy for storage
        cache_key = _get_reference_embeddings_cache_key(level, model_name)
        embeddings_dict[cache_key] = [
            emb.cpu().numpy() if hasattr(emb, 'cpu') else (emb.numpy() if hasattr(emb, 'numpy') else emb)
            for emb in embeddings
        ]
        
        # Save to disk
        with open(file_path, 'wb') as f:
            pickle.dump(embeddings_dict, f)
        
        print(f"💾 Cached reference embeddings for level: {level}")
    
    except Exception as e:
        print(f"⚠️ Failed to cache reference embeddings: {e}")

def get_or_create_reference_embeddings(level: str, references: List[str], model: SentenceTransformer) -> List:
    """Get cached reference embeddings or create and cache new ones."""
    # Try to get from cache first
    cached_embeddings = get_cached_reference_embeddings(level)
    if cached_embeddings is not None:
        # Convert cached numpy arrays back to tensors for comparison
        import torch
        return [torch.from_numpy(emb).float() for emb in cached_embeddings]
    
    # Generate new embeddings
    print(f"🔄 Generating reference embeddings for level: {level}")
    embeddings = []
    for reference in references:
        ref_embedding = model.encode(reference, convert_to_tensor=True)
        embeddings.append(ref_embedding)
    
    # Cache them (convert to numpy for storage)
    embeddings_np = [
        emb.cpu().numpy() if hasattr(emb, 'cpu') else (emb.numpy() if hasattr(emb, 'numpy') else emb)
        for emb in embeddings
    ]
    set_cached_reference_embeddings(level, embeddings_np)
    
    return embeddings

def get_cached_student_embedding(profile_text: str) -> Optional[np.ndarray]:
    """Retrieve cached student profile embedding if available."""
    cache_key = _get_profile_cache_key(profile_text)
    
    try:
        embedding = cache.get(cache_key)
        if embedding is not None:
            print(f"✅ Using cached student profile embedding")
            return embedding
    except Exception as e:
        print(f"⚠️ Error retrieving cached embedding: {e}")
    
    return None

def set_cached_student_embedding(profile_text: str, embedding: np.ndarray) -> None:
    """Cache student profile embedding."""
    cache_key = _get_profile_cache_key(profile_text)
    
    try:
        cache.set(cache_key, embedding)
        print(f"💾 Cached student profile embedding")
    except Exception as e:
        print(f"⚠️ Failed to cache embedding: {e}")

def get_or_create_student_embedding(profile_text: str, model: SentenceTransformer) -> np.ndarray:
    """Get cached student embedding or create and cache a new one."""
    # Try to get from cache first
    cached_embedding = get_cached_student_embedding(profile_text)
    if cached_embedding is not None:
        return cached_embedding
    
    # Generate new embedding
    print(f"🔄 Generating new student profile embedding")
    embedding = model.encode(profile_text, convert_to_tensor=True)
    
    # Convert to numpy for caching
    embedding_np = embedding.cpu().numpy() if hasattr(embedding, 'cpu') else embedding
    
    # Cache it
    set_cached_student_embedding(profile_text, embedding_np)
    
    return embedding

def generate_student_profile_embedding(profile_text: str, model: SentenceTransformer) -> np.ndarray:
    """Generate or retrieve cached student profile embedding."""
    # Get or create embedding (with caching)
    embedding = get_or_create_student_embedding(profile_text, model)
    
    # Return as numpy array
    return embedding if isinstance(embedding, np.ndarray) else embedding.cpu().numpy()

def compute_similarities(student_embedding: np.ndarray, issue_embeddings: np.ndarray) -> np.ndarray:
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([student_embedding], issue_embeddings)[0]

def rank_issues_by_similarity(
    issues: List[Dict], 
    student_embedding: np.ndarray, 
    issue_embeddings: np.ndarray
) -> List[Tuple[Dict, float]]:
    similarities = compute_similarities(student_embedding, issue_embeddings)
    ranked = list(zip(issues, similarities))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def recommend_issues(
    language: str = "all",
    per_page: int = 20,
    top_n: int = 100,
    student_profile: Optional[str] = None,
    model_name: str = 'all-MiniLM-L6-v2',
    use_phi: bool = True,
) -> List[Dict]:
    
    """Recommend GitHub issues based on student profile and experience level."""
    model = create_embedding_model(model_name)
    
    # 1. Extract programming language from profile if needed
    if student_profile and language == "all":
        language = extract_language_from_profile(student_profile, use_phi)
        print(f"Detected programming language from profile: {language}")

    # 2. Extract experience level from profile if needed
    if student_profile:
        experience_level = extract_experience_level_embeddings(student_profile, model, use_phi) # 'beginner', 'intermediate', 'advanced', or 'any'
        labels = EXPERIENCE_LEVEL_LABELS.get(experience_level, [])
        if labels:
            print(f"Found: {experience_level} with labels: {labels}")

    # 3. Fetch GitHub issues
        issues = fetch_github_issues(language, per_page, top_n, experience_level)
    
    # 4. Rank issues by similarity to student profile if provided
    if issues:
        issue_embeddings = generate_issue_embeddings(issues, model)
        student_embedding = generate_student_profile_embedding(student_profile, model)
        ranked_issues = rank_issues_by_similarity(issues, student_embedding, issue_embeddings)
        return [
            {
                **issue,
                "similarity": float(f"{score:.4f}")
            }
            for issue, score in ranked_issues
        ]
    else:
        return issues

def _get_cache_key(language: str, top_n: int) -> str:
    """Generate a unique cache key for language and top_n."""
    return f"issues_{language}_{top_n}"

def _is_cache_expired(cache_key: str) -> bool:
    """Check if cache entry has expired."""
    try:
        timestamp = cache.get(f"{cache_key}_timestamp")
        if timestamp is None:
            return True
        return time.time() - timestamp > CACHE_TTL
    except:
        return True

def get_cached_issues(language: str, top_n: int) -> Optional[List[Dict]]:
    """Retrieve cached issues if available and not expired."""
    cache_key = _get_cache_key(language, top_n)
    
    if _is_cache_expired(cache_key):
        return None
    
    try:
        issues = cache.get(cache_key)
        if issues:
            print(f"✅ Using cached issues for language: {language}, top_n: {top_n}")
            return issues
    except:
        pass
    
    return None

def set_cached_issues(language: str, top_n: int, issues: List[Dict]) -> None:
    """Cache issues with timestamp."""
    cache_key = _get_cache_key(language, top_n)
    
    try:
        cache.set(cache_key, issues)
        cache.set(f"{cache_key}_timestamp", time.time())
        print(f"💾 Cached {len(issues)} issues for language: {language}, top_n: {top_n}")
    except Exception as e:
        print(f"⚠️ Failed to cache issues: {e}")

def clear_profile_embeddings_cache() -> None:
    """Clear all cached student profile embeddings."""
    try:
        keys_to_delete = [key for key in cache.keys() if isinstance(key, str) and key.startswith("profile_embedding_")]
        for key in keys_to_delete:
            del cache[key]
        print(f"🗑️  Cleared {len(keys_to_delete)} cached profile embeddings")
    except Exception as e:
        print(f"⚠️ Error clearing profile embeddings cache: {e}")

def clear_reference_embeddings_cache() -> None:
    """Clear all cached reference embeddings."""
    try:
        file_path = _get_reference_embeddings_file_path()
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Cleared cached reference embeddings")
        else:
            print(f"ℹ️  No cached reference embeddings found")
    except Exception as e:
        print(f"⚠️ Error clearing reference embeddings cache: {e}")
