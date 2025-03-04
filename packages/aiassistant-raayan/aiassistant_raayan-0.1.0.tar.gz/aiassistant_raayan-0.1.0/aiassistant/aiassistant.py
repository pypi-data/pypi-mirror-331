"""
aiassistant.py

A module providing simple AI functionalities using Hugging Face Transformers.
It offers:
  - Sentiment Analysis
  - Text Summarization
  - Question Answering
"""

from transformers import pipeline

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The text to analyze.
    
    Returns:
        list: A list of dictionaries containing sentiment analysis results.
    """
    sentiment_pipeline = pipeline("sentiment-analysis")
    result = sentiment_pipeline(text)
    return result

def summarize_text(text, max_length=130, min_length=30):
    """
    Summarize the given text using a transformer model.

    Args:
        text (str): The text to summarize.
        max_length (int, optional): The maximum length of the summary. Defaults to 130.
        min_length (int, optional): The minimum length of the summary. Defaults to 30.
    
    Returns:
        str: The summarized text.
    """
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def answer_question(question, context):
    """
    Answer a question based on the provided context.

    Args:
        question (str): The question to answer.
        context (str): The context in which to answer the question.
    
    Returns:
        dict: A dictionary with the answer and related details.
    """
    qa_pipeline = pipeline("question-answering")
    result = qa_pipeline(question=question, context=context)
    return result
