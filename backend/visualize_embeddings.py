"""
Visualize experience level reference embeddings in 2D space.
"""

import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from core import EXPERIENCE_LEVEL_REFERENCES
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Load model
print("📦 Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for all reference examples
print("🔄 Generating embeddings for all reference examples...\n")

all_embeddings = []
all_labels = []
all_texts = []
colors = {'beginner': '#FF6B6B', 'intermediate': '#4ECDC4', 'advanced': '#45B7D1'}
level_colors = []

for level, examples in EXPERIENCE_LEVEL_REFERENCES.items():
    print(f"Processing {level.upper()} level...")
    for i, example in enumerate(examples, 1):
        embedding = model.encode(example, convert_to_tensor=False)
        all_embeddings.append(embedding)
        all_labels.append(f"{level.title()}")
        all_texts.append(example)
        level_colors.append(colors[level])
        print(f"  [{i}/10] {example[:60]}...")

all_embeddings = np.array(all_embeddings)
print(f"\n✅ Generated {len(all_embeddings)} embeddings\n")

# Reduce dimensionality with PCA first for speed
print("📉 Applying PCA dimensionality reduction...")
n_samples = all_embeddings.shape[0]
n_features = all_embeddings.shape[1]
n_pca_components = min(30, n_samples, n_features)
pca = PCA(n_components=n_pca_components)
embeddings_pca = pca.fit_transform(all_embeddings)
print(f"   PCA variance explained: {sum(pca.explained_variance_ratio_):.2%}\n")

# Apply t-SNE for final visualization
print("🎨 Applying t-SNE dimensionality reduction (this may take a minute)...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
embeddings_2d = tsne.fit_transform(embeddings_pca)
print("   ✅ t-SNE complete\n")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Plot 1: t-SNE with colors by experience level
print("📊 Creating visualizations...\n")

unique_labels = list(set(all_labels))
for label in unique_labels:
    mask = [l == label for l in all_labels]
    color = colors[label.lower()]
    ax1.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
               label=label, s=150, alpha=0.7, color=color, edgecolors='black', linewidth=1.5)

ax1.set_xlabel('t-SNE Dimension 1', fontsize=12, fontweight='bold')
ax1.set_ylabel('t-SNE Dimension 2', fontsize=12, fontweight='bold')
ax1.set_title('Experience Level Reference Embeddings (t-SNE)\nSemantic Space Visualization', 
             fontsize=14, fontweight='bold', pad=20)
ax1.legend(loc='best', fontsize=11, framealpha=0.95)
ax1.grid(True, alpha=0.3)

# Plot 2: Annotated with sample text
for i, (x, y, text, label) in enumerate(zip(embeddings_2d[:, 0], embeddings_2d[:, 1], all_texts, all_labels)):
    color = colors[label.lower()]
    ax2.scatter(x, y, s=150, alpha=0.7, color=color, edgecolors='black', linewidth=1.5)
    
    # Add abbreviated labels
    abbrev = text[:25] + "..." if len(text) > 25 else text
    ax2.annotate(f"{i+1}", (x, y), fontsize=8, ha='center', va='center', 
                fontweight='bold', color='white')

ax2.set_xlabel('t-SNE Dimension 1', fontsize=12, fontweight='bold')
ax2.set_ylabel('t-SNE Dimension 2', fontsize=12, fontweight='bold')
ax2.set_title('Numbered References (hover for details)\n1-10: Beginner, 11-20: Intermediate, 21-30: Advanced', 
             fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/gulatisukaran/Developer/Github_issues_recommendation_sys/backend/embeddings_visualization.png', 
           dpi=300, bbox_inches='tight')
print("✅ Visualization saved to: embeddings_visualization.png\n")

# Print statistics
print("=" * 70)
print("EMBEDDING STATISTICS")
print("=" * 70)
print(f"\n📊 Total References: {len(all_embeddings)}")
print(f"   • Beginner: 10")
print(f"   • Intermediate: {len([l for l in all_labels if 'Intermediate' in l])}")
print(f"   • Advanced: 10")
print(f"\n📐 Embedding Dimension: {all_embeddings.shape[1]}")
print(f"📉 PCA Components: 50")
print(f"🎨 t-SNE Output: 2D\n")

# Calculate pairwise distances within and between groups
from scipy.spatial.distance import pdist, squareform

distances = squareform(pdist(all_embeddings, metric='cosine'))

# Within-group distances (similarity)
beginner_idx = [i for i in range(10)]
intermediate_idx = [i for i in range(10, 20)]
advanced_idx = [i for i in range(20, 30)]

beginner_distances = [distances[i, j] for i in beginner_idx for j in beginner_idx if i < j]
intermediate_distances = [distances[i, j] for i in intermediate_idx for j in intermediate_idx if i < j]
advanced_distances = [distances[i, j] for i in advanced_idx for j in advanced_idx if i < j]

# Between-group distances (dissimilarity)
beginner_intermediate = [distances[i, j] for i in beginner_idx for j in intermediate_idx]
beginner_advanced = [distances[i, j] for i in beginner_idx for j in advanced_idx]
intermediate_advanced = [distances[i, j] for i in intermediate_idx for j in advanced_idx]

print("Within-Group Cohesion (lower = more similar):")
print(f"  🟢 Beginner:      {np.mean(beginner_distances):.4f} ± {np.std(beginner_distances):.4f}")
print(f"  🔵 Intermediate:  {np.mean(intermediate_distances):.4f} ± {np.std(intermediate_distances):.4f}")
print(f"  🟣 Advanced:      {np.mean(advanced_distances):.4f} ± {np.std(advanced_distances):.4f}")

print("\nBetween-Group Separation (higher = more different):")
print(f"  🟢→🔵 Beginner ↔ Intermediate: {np.mean(beginner_intermediate):.4f} ± {np.std(beginner_intermediate):.4f}")
print(f"  🟢→🟣 Beginner ↔ Advanced:     {np.mean(beginner_advanced):.4f} ± {np.std(beginner_advanced):.4f}")
print(f"  🔵→🟣 Intermediate ↔ Advanced: {np.mean(intermediate_advanced):.4f} ± {np.std(intermediate_advanced):.4f}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
print("""
✅ Good Separation: Groups that are far apart (high between-group distance)
   and internally cohesive (low within-group distance) are well-defined.

📊 Clustering Quality:
   • If groups form distinct clusters → Experience levels are well-separated
   • If groups overlap → Levels need better reference examples
   
🎯 What the visualization shows:
   • Position: Semantic meaning in embedding space
   • Color: Experience level (Red=Beginner, Teal=Intermediate, Blue=Advanced)
   • Proximity: Similar meanings are close, different meanings are far apart
""")
print("=" * 70)

plt.show()
