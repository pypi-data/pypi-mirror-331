# Webhook

Types:

```python
from avido.types import WebhookValidateResponse
```

Methods:

- <code title="post /v0/validate-webhook">client.webhook.<a href="./src/avido/resources/webhook.py">validate</a>(\*\*<a href="src/avido/types/webhook_validate_params.py">params</a>) -> <a href="./src/avido/types/webhook_validate_response.py">WebhookValidateResponse</a></code>

# Evaluations

Types:

```python
from avido.types import EvaluationCreateResponse, EvaluationRetrieveResponse, EvaluationListResponse
```

Methods:

- <code title="post /v0/evaluations">client.evaluations.<a href="./src/avido/resources/evaluations.py">create</a>(\*\*<a href="src/avido/types/evaluation_create_params.py">params</a>) -> <a href="./src/avido/types/evaluation_create_response.py">EvaluationCreateResponse</a></code>
- <code title="get /v0/evaluations/{id}">client.evaluations.<a href="./src/avido/resources/evaluations.py">retrieve</a>(id) -> <a href="./src/avido/types/evaluation_retrieve_response.py">EvaluationRetrieveResponse</a></code>
- <code title="get /v0/evaluations">client.evaluations.<a href="./src/avido/resources/evaluations.py">list</a>(\*\*<a href="src/avido/types/evaluation_list_params.py">params</a>) -> <a href="./src/avido/types/evaluation_list_response.py">SyncOffsetPagination[EvaluationListResponse]</a></code>

# Applications

Types:

```python
from avido.types import ApplicationRetrieveResponse, ApplicationListResponse
```

Methods:

- <code title="get /v0/applications/{id}">client.applications.<a href="./src/avido/resources/applications.py">retrieve</a>(id) -> <a href="./src/avido/types/application_retrieve_response.py">ApplicationRetrieveResponse</a></code>
- <code title="get /v0/applications">client.applications.<a href="./src/avido/resources/applications.py">list</a>(\*\*<a href="src/avido/types/application_list_params.py">params</a>) -> <a href="./src/avido/types/application_list_response.py">SyncOffsetPagination[ApplicationListResponse]</a></code>

# EvaluationTopics

Types:

```python
from avido.types import (
    EvaluationTopicCreateResponse,
    EvaluationTopicRetrieveResponse,
    EvaluationTopicListResponse,
)
```

Methods:

- <code title="post /v0/topics">client.evaluation_topics.<a href="./src/avido/resources/evaluation_topics.py">create</a>(\*\*<a href="src/avido/types/evaluation_topic_create_params.py">params</a>) -> <a href="./src/avido/types/evaluation_topic_create_response.py">EvaluationTopicCreateResponse</a></code>
- <code title="get /v0/topics/{id}">client.evaluation_topics.<a href="./src/avido/resources/evaluation_topics.py">retrieve</a>(id) -> <a href="./src/avido/types/evaluation_topic_retrieve_response.py">EvaluationTopicRetrieveResponse</a></code>
- <code title="get /v0/topics">client.evaluation_topics.<a href="./src/avido/resources/evaluation_topics.py">list</a>(\*\*<a href="src/avido/types/evaluation_topic_list_params.py">params</a>) -> <a href="./src/avido/types/evaluation_topic_list_response.py">SyncOffsetPagination[EvaluationTopicListResponse]</a></code>

# Tests

Types:

```python
from avido.types import TestRetrieveResponse, TestListResponse, TestRunResponse
```

Methods:

- <code title="get /v0/tests/{id}">client.tests.<a href="./src/avido/resources/tests.py">retrieve</a>(id) -> <a href="./src/avido/types/test_retrieve_response.py">TestRetrieveResponse</a></code>
- <code title="get /v0/tests">client.tests.<a href="./src/avido/resources/tests.py">list</a>(\*\*<a href="src/avido/types/test_list_params.py">params</a>) -> <a href="./src/avido/types/test_list_response.py">SyncOffsetPagination[TestListResponse]</a></code>
- <code title="post /v0/tests/run">client.tests.<a href="./src/avido/resources/tests.py">run</a>(\*\*<a href="src/avido/types/test_run_params.py">params</a>) -> <a href="./src/avido/types/test_run_response.py">TestRunResponse</a></code>

# Ingests

Types:

```python
from avido.types import IngestCreateResponse
```

Methods:

- <code title="post /v0/ingest">client.ingests.<a href="./src/avido/resources/ingests.py">create</a>(\*\*<a href="src/avido/types/ingest_create_params.py">params</a>) -> <a href="./src/avido/types/ingest_create_response.py">IngestCreateResponse</a></code>

# Threads

Types:

```python
from avido.types import ThreadRetrieveResponse, ThreadListResponse
```

Methods:

- <code title="get /v0/threads/{id}">client.threads.<a href="./src/avido/resources/threads.py">retrieve</a>(id) -> <a href="./src/avido/types/thread_retrieve_response.py">ThreadRetrieveResponse</a></code>
- <code title="get /v0/threads">client.threads.<a href="./src/avido/resources/threads.py">list</a>(\*\*<a href="src/avido/types/thread_list_params.py">params</a>) -> <a href="./src/avido/types/thread_list_response.py">ThreadListResponse</a></code>
