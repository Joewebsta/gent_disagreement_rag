"""Mock responses for external API calls."""

# Deepgram API mock responses
DEEPGRAM_SAMPLE_RESPONSE = {
    "metadata": {
        "transaction_key": "deprecated",
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "sha256": "sample_sha256",
        "created": "2025-01-15T10:00:00.000Z",
        "duration": 120.5,
        "channels": 1,
        "models": ["nova-3"],
        "model_info": {
            "nova-3": {
                "name": "nova-3",
                "version": "2024-01-09.29447",
                "uuid": "7607b7b9-4cf1-48a1-9200-1e8f50c6bbff",
                "batch": False,
                "streaming": False
            }
        }
    },
    "results": {
        "channels": [
            {
                "alternatives": [
                    {
                        "transcript": "Hello and welcome to A Gentleman's Disagreement. I'm your host Ricky Ghoshroy, and today I'm joined by Brendan Kelly to discuss an interesting topic.",
                        "confidence": 0.98756,
                        "words": [
                            {"word": "hello", "start": 0.0, "end": 0.5, "confidence": 0.99},
                            {"word": "and", "start": 0.5, "end": 0.7, "confidence": 0.95}
                        ],
                        "paragraphs": {
                            "transcript": "Hello and welcome to A Gentleman's Disagreement. I'm your host Ricky Ghoshroy, and today I'm joined by Brendan Kelly to discuss an interesting topic.",
                            "paragraphs": [
                                {
                                    "sentences": [
                                        {
                                            "text": "Hello and welcome to A Gentleman's Disagreement.",
                                            "start": 0.0,
                                            "end": 3.2
                                        },
                                        {
                                            "text": "I'm your host Ricky Ghoshroy, and today I'm joined by Brendan Kelly to discuss an interesting topic.",
                                            "start": 3.5,
                                            "end": 8.9
                                        }
                                    ],
                                    "start": 0.0,
                                    "end": 8.9,
                                    "num_words": 18,
                                    "speaker": "0"
                                },
                                {
                                    "sentences": [
                                        {
                                            "text": "Thanks for having me, Ricky.",
                                            "start": 9.0,
                                            "end": 10.5
                                        },
                                        {
                                            "text": "I'm excited to dive into this discussion.",
                                            "start": 10.8,
                                            "end": 13.2
                                        }
                                    ],
                                    "start": 9.0,
                                    "end": 13.2,
                                    "num_words": 12,
                                    "speaker": "1"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
}

# OpenAI embedding mock response
OPENAI_EMBEDDING_RESPONSE = {
    "object": "list",
    "data": [
        {
            "object": "embedding",
            "index": 0,
            "embedding": [
                -0.006929283495992422,
                -0.005336422007530928,
                0.014280156977474689,
                -0.01735618896782398,
                # ... (truncated for brevity, real response has 1536 dimensions)
                0.005123456789012345
            ] + [0.001] * 1530  # Fill to 1536 dimensions
        }
    ],
    "model": "text-embedding-3-small",
    "usage": {
        "prompt_tokens": 8,
        "total_tokens": 8
    }
}

# Error responses for testing
DEEPGRAM_ERROR_RESPONSE = {
    "error": {
        "message": "Invalid API key",
        "code": "INVALID_CREDENTIALS"
    }
}

OPENAI_ERROR_RESPONSE = {
    "error": {
        "message": "Invalid API key provided",
        "type": "invalid_request_error",
        "param": None,
        "code": "invalid_api_key"
    }
}