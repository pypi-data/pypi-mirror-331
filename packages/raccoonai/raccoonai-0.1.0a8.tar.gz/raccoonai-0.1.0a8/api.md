# Lam

Types:

```python
from raccoonai.types import LamRunResponse, LamTasksResponse
```

Methods:

- <code title="post /lam/run">client.lam.<a href="./src/raccoonai/resources/lam.py">run</a>(\*\*<a href="src/raccoonai/types/lam_run_params.py">params</a>) -> <a href="./src/raccoonai/types/lam_run_response.py">LamRunResponse</a></code>
- <code title="get /lam/tasks">client.lam.<a href="./src/raccoonai/resources/lam.py">tasks</a>(\*\*<a href="src/raccoonai/types/lam_tasks_params.py">params</a>) -> <a href="./src/raccoonai/types/lam_tasks_response.py">LamTasksResponse</a></code>

# Tail

Types:

```python
from raccoonai.types import TailUsersResponse
```

Methods:

- <code title="get /tail/users">client.tail.<a href="./src/raccoonai/resources/tail/tail.py">users</a>(\*\*<a href="src/raccoonai/types/tail_users_params.py">params</a>) -> <a href="./src/raccoonai/types/tail_users_response.py">TailUsersResponse</a></code>

## Apps

Types:

```python
from raccoonai.types.tail import AppAllResponse, AppLinkedResponse
```

Methods:

- <code title="get /tail/apps">client.tail.apps.<a href="./src/raccoonai/resources/tail/apps.py">all</a>() -> <a href="./src/raccoonai/types/tail/app_all_response.py">AppAllResponse</a></code>
- <code title="get /tail/linked-apps">client.tail.apps.<a href="./src/raccoonai/resources/tail/apps.py">linked</a>(\*\*<a href="src/raccoonai/types/tail/app_linked_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/app_linked_response.py">AppLinkedResponse</a></code>

## Auth

Types:

```python
from raccoonai.types.tail import AuthStatusResponse
```

Methods:

- <code title="get /tail/app/auth-status">client.tail.auth.<a href="./src/raccoonai/resources/tail/auth.py">status</a>(\*\*<a href="src/raccoonai/types/tail/auth_status_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/auth_status_response.py">AuthStatusResponse</a></code>

# Fleet

Types:

```python
from raccoonai.types import (
    FleetCreateResponse,
    FleetLogsResponse,
    FleetSessionsResponse,
    FleetStatusResponse,
    FleetTerminateResponse,
)
```

Methods:

- <code title="post /sessions/create">client.fleet.<a href="./src/raccoonai/resources/fleet.py">create</a>(\*\*<a href="src/raccoonai/types/fleet_create_params.py">params</a>) -> <a href="./src/raccoonai/types/fleet_create_response.py">FleetCreateResponse</a></code>
- <code title="get /sessions/{session_id}/logs">client.fleet.<a href="./src/raccoonai/resources/fleet.py">logs</a>(session_id) -> <a href="./src/raccoonai/types/fleet_logs_response.py">FleetLogsResponse</a></code>
- <code title="get /sessions">client.fleet.<a href="./src/raccoonai/resources/fleet.py">sessions</a>(\*\*<a href="src/raccoonai/types/fleet_sessions_params.py">params</a>) -> <a href="./src/raccoonai/types/fleet_sessions_response.py">FleetSessionsResponse</a></code>
- <code title="get /sessions/{session_id}/status">client.fleet.<a href="./src/raccoonai/resources/fleet.py">status</a>(session_id) -> <a href="./src/raccoonai/types/fleet_status_response.py">FleetStatusResponse</a></code>
- <code title="delete /sessions/{session_id}/terminate">client.fleet.<a href="./src/raccoonai/resources/fleet.py">terminate</a>(session_id) -> <a href="./src/raccoonai/types/fleet_terminate_response.py">FleetTerminateResponse</a></code>

# Extensions

Types:

```python
from raccoonai.types import (
    ExtensionDeleteResponse,
    ExtensionAllResponse,
    ExtensionGetResponse,
    ExtensionUploadResponse,
)
```

Methods:

- <code title="delete /extensions/{extensionId}">client.extensions.<a href="./src/raccoonai/resources/extensions.py">delete</a>(extension_id) -> <a href="./src/raccoonai/types/extension_delete_response.py">object</a></code>
- <code title="get /extensions">client.extensions.<a href="./src/raccoonai/resources/extensions.py">all</a>() -> <a href="./src/raccoonai/types/extension_all_response.py">ExtensionAllResponse</a></code>
- <code title="get /extensions/{extensionId}">client.extensions.<a href="./src/raccoonai/resources/extensions.py">get</a>(extension_id) -> <a href="./src/raccoonai/types/extension_get_response.py">ExtensionGetResponse</a></code>
- <code title="post /extensions">client.extensions.<a href="./src/raccoonai/resources/extensions.py">upload</a>(\*\*<a href="src/raccoonai/types/extension_upload_params.py">params</a>) -> <a href="./src/raccoonai/types/extension_upload_response.py">ExtensionUploadResponse</a></code>
