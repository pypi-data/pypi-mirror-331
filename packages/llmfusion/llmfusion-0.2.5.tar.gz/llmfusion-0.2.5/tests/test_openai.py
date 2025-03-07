
# ----- testing/test_openai.py -----
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        client = Mock()
        mock.return_value = client
        yield client


def test_openai_generate(mock_openai):
    from llm_providers import OpenAIClient, LLMConfig

    config = LLMConfig(api_key="test", model_name="gpt-4")
    client = OpenAIClient(config)

    mock_response = Mock()
    mock_response.choices[0].message.content = "Test response"
    mock_openai.chat.completions.create.return_value = mock_response

    input = LLMInput(prompt="Test")
    response = client.generate(input)

    assert response == "Test response"
    mock_openai.chat.completions.create.assert_called_once()