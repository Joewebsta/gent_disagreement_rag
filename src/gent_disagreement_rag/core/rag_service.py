from .vector_search import VectorSearch
from openai import OpenAI
import os


class RAGService:
    """Handles RAG operations"""

    # Default search parameters
    DEFAULT_THRESHOLD = 0.5
    DEFAULT_LIMIT = 5

    def __init__(self, database_name="gent_disagreement"):
        self.vector_search = VectorSearch(database_name)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def ask_question(self, question, model="gpt-4o-mini"):
        """Implement RAG to answer questions using retrieved context"""
        try:
            # 1. Find relevant transcript segments
            # search_results = self.vector_search.find_similar_above_threshold(
            #     question, threshold=self.DEFAULT_THRESHOLD, limit=self.DEFAULT_LIMIT
            # )

            search_results = self.vector_search.find_most_similar(
                question, limit=self.DEFAULT_LIMIT
            )

            # 2. Format context from search results
            formatted_results = self._format_search_results(search_results)

            # 3. Create prompt with context
            prompt = self._create_prompt(formatted_results, question)

            # 4. Generate response
            return self._generate_response(prompt, model)

        except Exception as e:
            print(f"Error in RAG service: {e}")
            raise e

    def _generate_response(self, prompt, model):
        """Generate response using OpenAI LLM"""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _format_search_results(self, search_results):
        """Format the search results into readable string"""

        formatted_result = ""
        for result in search_results:
            formatted_result += f"Speaker: {result['speaker']}\n"
            formatted_result += f"Text: {result['text']}\n"
            formatted_result += f"Similarity: {result['similarity']}\n  "
            formatted_result += f"--------------------------------\n"

        return formatted_result

    def _create_prompt(self, formatted_results, question):
        """Create the prompt for the LLM."""
        return f"""# A Gentleman's Disagreement Podcast Analysis

You are an expert analyst of **A Gentleman's Disagreement Podcast**. Your task is to provide insightful answers based on the provided transcript segments.

## Instructions
- Use the relevant transcript segments below to answer the user's question
- If the segments aren't relevant to the question, clearly state this
- Maintain the conversational tone of the podcast in your analysis

## Available Transcript Segments
{formatted_results}

## User Question
**{question}**

## Your Response
Please provide a comprehensive answer based on the transcript segments and your knowledge of the podcast:"""


# - Provide specific quotes and references when possible
