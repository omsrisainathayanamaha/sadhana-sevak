# Processes queries that come through the API.

import mistralai
import backend_constants
import pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
import os

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


model = SentenceTransformer(backend_constants.SENTENCE_TRANSFORMER_MODEL)


def context_search(query: str, top_k: int = 3) -> str:
    print("Searching for context...")
    queryVector = model.encode(query, convert_to_numpy = True).tolist()
    results = index.query(queries = queryVector, top_k = top_k)
    print("Results: ", results)
    return [{"text": match['metadata']['text'], "score": match['score']} for match in results['matches']]

def get_commentaries(query):
    print("Getting commentaries...")
    return context_search(query)


def synthesize_answer(query:str) -> str:
    print("Synthesizing answer...")
    commentary = get_commentaries(query)
    context_text = "\n".join(commentary)
    prompt = f"""
    The user asked: "{query}"
    Based on the following context, provide a concise and informative answer:
    {context_text}
    """
    print("Prompt: ", prompt)
    try:
        print("Generating response...")
        chat_response = mistral.chat.complete(
            model = backend_constants.MISTRAL_MODEL,
            messages = [
                {   
                    "role": "user",
                    "content": prompt
                },
            ]
        )
        print("Response: ", chat_response.choices[0].message.content)
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response, query_processor."

    




