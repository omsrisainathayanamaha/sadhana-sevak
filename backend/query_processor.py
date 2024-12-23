# Processes queries that come through the API.

import mistralai
import backend_constants
import pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import time

mistral = mistralai.Mistral(api_key=backend_constants.MISTRAL_API_KEY)
pc = pinecone.Pinecone(api_key=backend_constants.PINECONE_API_KEY)
if backend_constants.PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=backend_constants.PINECONE_INDEX_NAME,
        dimension=1024,
        metric='cosine',
        spec=pinecone.ServerlessSpec(cloud='aws', region=backend_constants.PINECONE_ENVIRONMENT)
    )


index = pc.Index(backend_constants.PINECONE_INDEX_NAME)
ai = mistralai.Mistral(api_key=backend_constants.MISTRAL_API_KEY)

model = SentenceTransformer(backend_constants.SENTENCE_TRANSFORMER_MODEL)
"""
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
def context_search(query: str, top_k: int = 3) -> str:
    print("Searching for context...")
    queryVector = embed([query])[0].embedding
    qv = ({"id": "question", "values": queryVector[0], "metadata": {"text": query.strip()}})
    results = index.query(queries = qv, top_k = top_k)
    print("Results: ", results)
    return [{"text": match['metadata']['text'], "score": match['score']} for match in results['matches']]

"""
import time
import pinecone

def embed(document: list[str], delay=2, max_retries=5) -> list[list[float]]:
    
    print("Embedding document...")
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}")
            # Replace this with the actual call to your embedding model
            embeddings = ai.embeddings.create(model="mistral-embed", inputs=document)

            # Ensure embeddings are in the correct format
            if hasattr(embeddings, 'data') and isinstance(embeddings.data, list):
                print("Returning embeddings...")
                return list(embeddings.data)

            raise ValueError("Embeddings format unexpected")
        except Exception as e:
            print(f"Error: {e}, retrying...")
            time.sleep(delay)
    raise RuntimeError("Failed to embed document after maximum retries.")

def context_search(query: str, top_k: int = 1) -> str:
    print("Performing similarity search...")
    try:
        # Generate the embedding for the query
        query_vector = embed([query])[0].embedding  # Single embedding for the query
        
        print("Getting search results...")
        query_results = index.query(
            vector=query_vector,  
            top_k=top_k,          
            include_metadata=True,
            namespace='sahasta' 
        )
        print("Results: ", query_results)
        
        
        
        return query_results["matches"][0]["metadata"]["text"]  
        
    except Exception as e:
        print(f"Search error: {e}")
        return []
#"""
def get_commentaries(query):
    print("Getting commentaries...")
    return context_search(query)


import tiktoken  # Tokenizer to count tokens (or use another token counting library)

def tokenize(text: str) -> list[str]:
    """Tokenizes the input text and returns a list of tokens."""
    # Use tiktoken or a similar library to tokenize the text.
    # This example assumes a tokenizer is available.
    tokenizer = tiktoken.get_encoding("cl100k_base")  # Replace with your model's tokenizer
    return tokenizer.encode(text)

def detokenize(tokens: list[int]) -> str:
    """Detokenizes a list of tokens back into a string."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    return tokenizer.decode(tokens)

def split_into_chunks(text: str, max_tokens: int = 1000) -> list[str]:
    """Splits text into chunks of approximately max_tokens length."""
    tokens = tokenize(text)
    chunks = []
    while tokens:
        chunk = tokens[:max_tokens]
        tokens = tokens[max_tokens:]
        chunks.append(detokenize(chunk))
    return chunks

def synthesize_answer(query: str) -> str:
    print("Synthesizing answer...")

    # Step 1: Retrieve commentaries and join into context
    commentary = get_commentaries(query)
    context_text = "\n".join(commentary)

    # Step 2: Split context into 4000-token chunks
    context_chunks = split_into_chunks(context_text)

    # Step 3: Iterate over chunks and generate responses
    responses = []
    for chunk in context_chunks:
        prompt = f"""
        The user asked: "{query}"
        Based on the following context by Gurudev, provide a concise and informative answer that is in accordance with the teachings of Gurudev. Make it so that it sounds like Gurudev's own tone. Use ONLY English words, and avoid citing the text directly. Format your answer in a well formatted manner.:
        {chunk}
        """
        print("Prompt: ", prompt)
        try:
            print("Generating response...")
            chat_response = mistral.chat.complete(
                model=backend_constants.MISTRAL_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    },
                ]
            )
            response = chat_response.choices[0].message.content
            print("Response: ", response)
            responses.append(response)
        except Exception as e:
            print(f"Error generating response for chunk: {e}")
            #responses.append("An error occurred while generating the response for this chunk.")
    final = " ".join(responses)
    #print("Cleaning up final response...")
    finala = mistral.chat.complete(model = backend_constants.MISTRAL_MODEL, messages = [{"role": "user", "content": f"The following is an answer to the question of a person. Do not modify the answer. Just correct it for cohesion, conciseness, nonrepetition, formatting, and clarity. Do not leave a trace of what you have done. Only give me the final content. Keep the initial, letter-like format in the format of Swami Chinmayananda. {final}"}])
    return finala.choices[0].message.content
