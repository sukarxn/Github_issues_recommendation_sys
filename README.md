# GitHub Issues Recommendation System

A Python-based recommendation system that fetches "good first issue" labeled issues from the most popular GitHub repositories and ranks them based on similarity to a student's profile using sentence embeddings.

## 🎯 Features

- **Fetch from Top Repositories**: Retrieves issues from the most popular GitHub repositories (by stars)
- **Smart Filtering**: Filters by programming language and "good first issue" labels
- **AI-Powered Matching**: Uses sentence transformers to generate embeddings and rank issues by similarity to student profiles
- **Flexible Input**: Accepts student profiles as text or file paths
- **GitHub API Integration**: Authenticated requests with rate limit handling
- **Customizable**: Configure number of issues, repositories, and programming languages

## 📋 Requirements

- Python 3.12+ (tested with 3.12.8)
- GitHub Personal Access Token (for higher API rate limits)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Github_issues_recommendation_sys
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install requests sentence-transformers scikit-learn python-dotenv numpy
```

### 4. Set up GitHub Token

Create a `.env` file in the project root:

```bash
GITHUB_TOKEN=your_github_personal_access_token_here
```

**To generate a token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "GitHub Issues Recommendation")
4. Select scope: `public_repo`
5. Generate and copy the token
6. Paste it in your `.env` file

> ⚠️ **Important**: Never commit the `.env` file to version control!

## 📖 Usage

### Basic Usage (without student profile)

Fetch and list issues without ranking:

```bash
python main.py -l python -n 20 --top-n 50
```

### With Student Profile (Ranked by Similarity)

Create a student profile file (`student_profile.txt`):

```text
I am a computer science student with strong skills in Python and web development. 
I have experience with Django, Flask, and FastAPI frameworks. 
I'm interested in contributing to open-source projects related to data science, 
machine learning, and API development.
```

Run with profile:

```bash
python main.py -n 15 --top-n 50 -p student_profile.txt
```

### Command-Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--language` | `-l` | `all` | Programming language filter (e.g., `python`, `javascript`, `all`) |
| `--per-page` | `-n` | `20` | Total number of issues to fetch |
| `--top-n` | | `100` | Number of top repositories to search (max 100) |
| `--student-profile` | `-p` | None | Path to student profile file or inline text |
| `--model` | `-m` | `all-MiniLM-L6-v2` | SentenceTransformer model name |

### Example Commands

**Fetch Python issues from top 100 repos:**
```bash
python main.py -l python -n 25 --top-n 100
```

**Get JavaScript issues ranked by profile:**
```bash
python main.py -l javascript -n 10 -p my_profile.txt
```

**Use inline profile text:**
```bash
python main.py -n 10 -p "I'm a beginner developer interested in Python web frameworks"
```

**Search all languages:**
```bash
python main.py -n 20
```

## 🏗️ Project Structure

```
Github_issues_recommendation_sys/
├── .env                    # Environment variables (GitHub token)
├── .gitignore             # Git ignore rules
├── .venv/                 # Virtual environment
├── main.py                # Main application script
├── sample_profile.txt     # Example student profile
└── README.md              # This file
```

## 🔧 How It Works

### 1. **Fetch Top Repositories**
   - Queries GitHub Search API for most starred repositories
   - Optionally filters by programming language
   - Returns top N repositories (default: 100)

### 2. **Extract "Good First Issues"**
   - For each repository, fetches open issues
   - Filters for labels: "good first issue" or "good-first-issue"
   - Excludes pull requests

### 3. **Generate Embeddings** (if profile provided)
   - Uses `SentenceTransformer` model (`all-MiniLM-L6-v2`)
   - Generates embeddings for issue text (title + body)
   - Generates embedding for student profile

### 4. **Compute Similarity & Rank**
   - Calculates cosine similarity between profile and each issue
   - Ranks issues by similarity score (higher = more relevant)
   - Returns top matches

### 5. **Display Results**
   - Prints issues with repository name, title, URL
   - Shows similarity scores if ranked

## 📊 Sample Output

### Without Profile:
```
1. [vuejs/vue] Warn if colon shorthand is used on v-if/v-html/etc.
   https://github.com/vuejs/vue/issues/10191
2. [tensorflow/tensorflow] Add support for custom metrics
   https://github.com/tensorflow/tensorflow/issues/54321
```

### With Profile (Ranked):
```
Loading embedding model...
Generating embeddings...
Ranking issues by similarity...

1. [avelino/awesome-go] few projects that can be added (similarity: 0.3911)
   https://github.com/avelino/awesome-go/issues/5563
2. [practical-tutorials/project-based-learning] Clean up dead or outdated tutorials (similarity: 0.2813)
   https://github.com/practical-tutorials/project-based-learning/issues/344
```

## 🧠 AI/ML Components

### Sentence Transformers
- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Purpose**: Converts text to vector representations
- **Cache Location**: `~/.cache/torch/sentence_transformers/`

### Similarity Computation
- **Method**: Cosine similarity
- **Library**: scikit-learn
- **Range**: -1 to 1 (higher = more similar)

## ⚙️ Configuration

### Rate Limits

| Authentication | Rate Limit | Recommended `--top-n` |
|---------------|------------|---------------------|
| No Token | 60 requests/hour | ≤ 30 |
| With Token | 5,000 requests/hour | Up to 100 |

Without a token, the script automatically limits repository count to avoid rate limit errors.

### Model Cache

SentenceTransformer models are cached in:
```
~/.cache/torch/sentence_transformers/
```

To change the cache location, set in `.env`:
```
SENTENCE_TRANSFORMERS_HOME=/custom/path/to/models
```

## 🐛 Troubleshooting

### Rate Limit Exceeded (403 Error)
**Problem**: `403 Client Error: rate limit exceeded`

**Solutions**:
1. Add a valid `GITHUB_TOKEN` to `.env`
2. Reduce `--top-n` parameter
3. Wait for rate limit to reset (check: https://api.github.com/rate_limit)

### No Issues Found
**Problem**: Script returns no issues

**Causes**:
- Repositories may not have "good first issue" labels
- Try increasing `--top-n` or removing language filter
- Try different programming languages

### Import Errors
**Problem**: `ModuleNotFoundError`

**Solution**: Install missing dependencies:
```bash
pip install requests sentence-transformers scikit-learn python-dotenv numpy
```

## 📦 Dependencies

- **requests**: HTTP library for GitHub API calls
- **sentence-transformers**: Generate text embeddings
- **scikit-learn**: Compute cosine similarity
- **python-dotenv**: Load environment variables from `.env`
- **numpy**: Array operations for embeddings

## 🔐 Security Notes

- **Never commit** `.env` files or tokens to version control
- `.env` is already in `.gitignore`
- Revoke tokens immediately if exposed
- Use fine-grained tokens with minimal scopes

## 🚧 Current Limitations

- Maximum 100 repositories per query (GitHub API limit)
- Only searches open issues (not closed ones)
- Requires internet connection for API calls and model downloads
- First run downloads ~90MB model (cached for future use)

## 🛣️ Future Enhancements

- [ ] Add caching for fetched issues
- [ ] Support for multiple student profiles
- [ ] Export results to CSV/JSON
- [ ] Add filtering by issue age, comment count, etc.
- [ ] Web interface for easier interaction
- [ ] Fine-tune embeddings on GitHub issues data
- [ ] Add repository README context to recommendations

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Project Status**: ✅ Functional - Core features implemented and tested

**Last Updated**: October 16, 2025
