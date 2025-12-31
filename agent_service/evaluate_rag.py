import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
    )
    from datasets import Dataset
    from langchain_groq import ChatGroq
    from langchain_cohere import CohereEmbeddings
except ImportError as e:
    logger.error(f"Failed to import Ragas dependencies: {e}")
    logger.error("Please ensure 'ragas', 'datasets', and 'langchain-cohere' are installed.")
    exit(1)

def run_evaluation():
    """
    Run Ragas evaluation on a sample dataset using Groq LLM and Cohere embeddings.
    """
    logger.info("Starting Ragas evaluation setup...")

    # 1. Setup LLM (Judge)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment")

    # Initialize Groq LLM for Ragas "Judge"
    # wrapper for Ragas to use
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    # 2. Setup Embeddings (for relevance metrics)
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        raise ValueError("COHERE_API_KEY not found in environment")
    
    embeddings = CohereEmbeddings(
        cohere_api_key=cohere_api_key,
        model="embed-english-v3.0"
    )

    # 3. Create Sample Dataset
    # (Question, Answer, Retrieved Contexts, Ground Truth)
    # Using a sample scenario from the portfolio knowledge base
    data = {
        'question': [
            'What technology is used for the backend?',
            'How is the frontend deployed?',
            'What vector database is used?'
        ],
        'answer': [
            'The backend is built using Django and Django REST Framework.',
            'The frontend is a Next.js application deployed in a Docker container.',
            'The project uses PostgreSQL with the pgvector extension.'
        ],
        'contexts': [
            ['The project consists of a Django REST backend...', 'Backend: Django + Django REST Framework'],
            ['Frontend (/frontend): Next.js 16.0.5... Deployment: Fully Dockerized'],
            ['Database: PostgreSQL with pgvector extension... Vector Embeddings: Cohere']
        ],
        'ground_truth': [
            'Django and Django REST Framework are used for the backend.',
            'The frontend uses Next.js and is containerized with Docker.',
            'PostgreSQL with pgvector is used for the vector database.'
        ]
    }

    dataset = Dataset.from_dict(data)
    logger.info(f"Created dataset with {len(data['question'])} samples")

    # 4. Run Evaluation
    logger.info("Running evaluation with Ragas...")
    
    # Define metrics to calculate
    # Faithfulness: Factual consistency of answer to context
    # Answer Relevancy: How pertinent the answer is to the question
    # Context Precision: Signal-to-noise ratio of retrieved context
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
    ]

    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings
    )

    # 5. Output Results
    logger.info("\n=== Ragas Evaluation Report ===")
    logger.info(results)
    
    # Save results to file
    df = results.to_pandas()
    output_file = "ragas_report.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"Detailed results saved to {output_file}")

if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        exit(1)
