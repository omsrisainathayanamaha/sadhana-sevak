import pinecone
import numpy as np
from mistralai import Mistral
import backend_constants
import sys
import json
import os
import time
import float_flattening_utils

def vectorize_commentary():
    pc = pinecone.Pinecone(api_key=backend_constants.PINECONE_API_KEY, env="us-east1-aws")

    if backend_constants.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            backend_constants.PINECONE_INDEX_NAME,
            1024,
            spec=pinecone.ServerlessSpec("aws", backend_constants.PINECONE_ENVIRONMENT),
            metric="cosine"
        )
    index = pc.Index(backend_constants.PINECONE_INDEX_NAME)

    # Load processed_text.txt
    with open('processed_text.txt', 'r') as f:
        commentary = f.readlines()
    print("Commentary Length:", len(commentary))

    ai = Mistral(api_key=backend_constants.MISTRAL_API_KEY)

    """
    def embed(document: list[str]) -> list[list[float]]:
        embeddings = ai.embeddings.create(model="mistral-embed", inputs=document)
        time.sleep(1.5)
        return embeddings.data
    """
    import requests

    def embed(document: list[str], delay=2, max_retries=5) -> list[list[float]]:
        print("Embedding document...")
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}")
                embeddings = ai.embeddings.create(model="mistral-embed", inputs=document)
                print("Sleeping...")
                time.sleep(delay)
                print("Returning embeddings...")
                return embeddings.data
            except Exception as e:
                print(f"HTTP error: {e}")
                
                    
                retry_after = int(e.response.headers.get("Retry-After", delay))
                print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            except Exception as e:
                print(f"Error embedding document: {e}")
                raise e

    def split_into_batches(lines, max_tokens=16384):
        current_batch = []
        current_token_count = 0
        tokens_per_line = max_tokens // 50  # Start with a default tokens per line limit
    
        for line in lines:
            tokens_in_line = len(line.split())
        
            if tokens_in_line > tokens_per_line:
                # If a line has too many tokens, split it further
                num_splits = (tokens_in_line + tokens_per_line - 1) // tokens_per_line
                for a in range(num_splits):
                    split_line = line[:tokens_per_line]
                    current_batch.append(split_line)
                    yield current_batch
                    current_batch = []
                    current_token_count = 0
            elif current_token_count + tokens_in_line > max_tokens:
                yield current_batch
                current_batch = []
                current_token_count = 0
            else:
                current_batch.append(line)
                current_token_count += tokens_in_line
    
        if current_batch:
            yield current_batch



    batches = list(split_into_batches(commentary, max_tokens=6000))
    print(f"Split commentary into {len(batches)} batches.")
    embeddings = []
    counter = 0
    for batch in batches:
        print(f"Processing batch {counter + 1}...")
        counter += 1
        try:
            batch_embeddings = embed(batch)
            embeddings.extend([e.embedding for e in batch_embeddings])
        except Exception as a:
            print(f"Error processing batch: {a}")

    vectors = []
    for i, (comment, embedding) in enumerate(zip(commentary, embeddings)):
        #vector_flat = embedding.flatten().tolist()
        vectors.append({"id": f"vec{i+1}", "values": embedding, "metadata": {"text": comment.strip()}})

    def calculate_vector_size(vector):
        return sys.getsizeof(vector)

    def chunk_vectors_dynamic(vectors, max_bytes=4194304):
        current_chunk = []
        current_chunk_size = 0
        for vector in vectors:
            vector_size = calculate_vector_size(vector)
            if current_chunk_size + vector_size > max_bytes:
                yield current_chunk
                current_chunk = []
                current_chunk_size = 0
            current_chunk.append(vector)
            current_chunk_size += vector_size
        if current_chunk:
            yield current_chunk

    vector_chunks = list(chunk_vectors_dynamic(vectors, max_bytes=4194304))

    for chunk in vector_chunks:
        try:
            index.upsert(vectors=chunk, namespace="sahasta")
            print(f"Successfully upserted a chunk of {len(chunk)} vectors.")
        except Exception as e:
            print(f"Error upserting chunk: {e}")

    
    print("Vectorization exited.")