from .rag_service import RAGService


class ChatManager:
    def __init__(self):
        self.rag_service = RAGService()

    def run(self):
        print("Welcome to the A Gentleman's Disagreement Chatbot!")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("-" * 50)

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            print("Thinking...")

            # Get the search results and response
            response, search_results = self.rag_service.ask_question_with_context(
                user_input
            )

            # Display retrieved context
            if search_results:
                print("\n📚 Retrieved Context:")
                print("=" * 50)
                for i, result in enumerate(search_results, 1):
                    confidence = result.get("similarity", 0)
                    confidence_percentage = f"{confidence * 100:.1f}%"
                    print(f"{i}. Speaker: {result['speaker']}")
                    print(f"   Confidence: {confidence_percentage}")
                    print(f"   Episode: {result['episode_number']}")
                    print(f"   Title: {result['title']}")
                    print(f"   Date Published: {result['date_published']}")
                    print(
                        f"   Text: {result['text'][:200]}{'...' if len(result['text']) > 200 else ''}"
                    )
                    print()
                print("=" * 50)

            print(f"Assistant: {response}")
            print("-" * 50)
