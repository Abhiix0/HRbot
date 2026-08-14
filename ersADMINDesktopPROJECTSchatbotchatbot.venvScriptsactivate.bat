[1mdiff --cc tests/core/test_service.py[m
[1mindex 522146e,fa72976..0000000[m
[1m--- a/tests/core/test_service.py[m
[1m+++ b/tests/core/test_service.py[m
[36m@@@ -1,45 -1,53 +1,95 @@@[m
[31m -from unittest.mock import patch[m
[32m +from unittest.mock import MagicMock, patch[m
  [m
[32m++<<<<<<< HEAD[m
[32m +from hrbot.core import service[m
[32m +[m
[32m +[m
[32m +def _patch_common(response_text: str = "Hello!"):[m
[32m +    fake_provider = MagicMock()[m
[32m +    fake_provider.generate.return_value = response_text[m
[32m +    return ([m
[32m +        patch.object(service, "get_provider", return_value=fake_provider),[m
[32m +        patch.object(service, "get_system_prompt", return_value="You are helpful."),[m
[32m +        patch.object(service.retriever, "search", return_value=""),[m
[32m +    )[m
[32m +[m
[32m +[m
[32m +def test_get_response_returns_string():[m
[32m +    patches = _patch_common("Hello!")[m
[32m +    with patches[0], patches[1], patches[2]:[m
[32m +        result = service.get_response("Hi")[m
[32m++=======[m
[32m+ from hrbot.core.service import get_response[m
[32m+ from hrbot.knowledge.schema import RetrievalResult[m
[32m+ [m
[32m+ [m
[32m+ def test_get_response_returns_string():[m
[32m+     mock_result = RetrievalResult([m
[32m+         query="Hi",[m
[32m+         matches=[],[m
[32m+         top_score=0.0,[m
[32m+         confidence="none",[m
[32m+     )[m
[32m+     with ([m
[32m+         patch("hrbot.core.service.get_llm_response", return_value="Hello!"),[m
[32m+         patch("hrbot.core.service.get_system_prompt", return_value="You are helpful."),[m
[32m+         patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),[m
[32m+     ):[m
[32m+         result = get_response("Hi")[m
[32m++>>>>>>> 35f38479f6bc29ae22a75d99b62394baf1e52afe[m
      assert isinstance(result, str)[m
      assert result == "Hello!"[m
  [m
  [m
  def test_generate_response_mock():[m
[32m++<<<<<<< HEAD[m
[32m +    patches = _patch_common("Mocked response")[m
[32m +    with patches[0], patches[1], patches[2]:[m
[32m +        result = service.get_response("test input")[m
[32m++=======[m
[32m+     mock_result = RetrievalResult([m
[32m+         query="test input",[m
[32m+         matches=[],[m
[32m+         top_score=0.0,[m
[32m+         confidence="none",[m
[32m+     )[m
[32m+     with ([m
[32m+         patch("hrbot.core.service.get_llm_response", return_value="Mocked response"),[m
[32m+         patch("hrbot.core.service.get_system_prompt", return_value="prompt"),[m
[32m+         patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),[m
[32m+     ):[m
[32m+         result = get_response("test input")[m
[32m++>>>>>>> 35f38479f6bc29ae22a75d99b62394baf1e52afe[m
      assert result == "Mocked response"[m
  [m
  [m
  def test_get_response_non_empty():[m
[32m++<<<<<<< HEAD[m
[32m +    patches = _patch_common("Sure!")[m
[32m +    with patches[0], patches[1], patches[2]:[m
[32m +        result = service.get_response("Tell me something")[m
[32m++=======[m
[32m+     mock_result = RetrievalResult([m
[32m+         query="Tell me something",[m
[32m+         matches=[],[m
[32m+         top_score=0.0,[m
[32m+         confidence="none",[m
[32m+     )[m
[32m+     with ([m
[32m+         patch("hrbot.core.service.get_llm_response", return_value="Sure!"),[m
[32m+         patch("hrbot.core.service.get_system_prompt", return_value="prompt"),[m
[32m+         patch("hrbot.core.service.retriever.retrieve", return_value=mock_result),[m
[32m+     ):[m
[32m+         result = get_response("Tell me something")[m
[32m++>>>>>>> 35f38479f6bc29ae22a75d99b62394baf1e52afe[m
      assert result != ""[m
[32m +[m
[32m +[m
[32m +def test_get_response_updates_history():[m
[32m +    patches = _patch_common("Answer")[m
[32m +    with patches[0], patches[1], patches[2]:[m
[32m +        service.get_response("What are the hours?")[m
[32m +    history = service.get_history()[m
[32m +    assert history[-2].role == "user"[m
[32m +    assert history[-1].role == "assistant"[m
[32m +    assert history[-1].content == "Answer"[m
