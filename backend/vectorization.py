import pinecone
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pinecone.init(api_key='YOUR_PINECONE_API_KEY', environment='us-west1-gcp')

# Create a Pinecone index
index_name = 'bhagavad-gita-commentary'
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=768)

# Connect to the index
index = pinecone.Index(index_name)

# Load the commentary array from a separate file
commentary = [
    "Commentary on verse 1",
    "Commentary on verse 2",
    # Add more commentary here
]

# Initialize the sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Vectorize and store the commentary
for i, comment in enumerate(commentary):
    vector = model.encode(comment).tolist()
    index.upsert([(f'verse-{i+1}', vector)])

print("Commentary has been vectorized and stored in Pinecone.")