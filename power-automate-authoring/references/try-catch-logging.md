# Power Automate TRY/CATCH Logging

These snippets are generic templates for cloud flow workflow JSON. Rename actions and variables to match the target flow. Keep connector-specific actions, recipients, and log destinations project-defined.

Default to concise alerting. Email should contain an operational summary only; raw connector outputs can contain personal data, document contents, SQL rows, HTTP payloads, or other sensitive values. Store detailed payloads only in an approved log destination and truncate raw TRY results by default.

## Required Shape

Use a business scope named `TRY_<domain>`, then a catch scope named `CATCH_<domain>`.

```json
"CATCH_<domain>": {
  "type": "Scope",
  "actions": {},
  "runAfter": {
    "TRY_<domain>": [
      "Failed",
      "TimedOut"
    ]
  }
}
```

Add `Skipped` to `runAfter` only if a skipped TRY scope should send an alert. Do not use `Cancelled` in `runAfter`; Power Automate run-after statuses are `Succeeded`, `Failed`, `Skipped`, and `TimedOut`.

## Minimal Catch Actions

Inside `CATCH_<domain>`, add these actions before sending email or writing to a log store.

```json
"Compose_catch_try_result": {
  "type": "Compose",
  "inputs": "@result('TRY_<domain>')"
},
"Filter_catch_failed_actions": {
  "type": "Query",
  "inputs": {
    "from": "@outputs('Compose_catch_try_result')",
    "where": "@or(equals(item()?['status'], 'Failed'), equals(item()?['status'], 'TimedOut'))"
  },
  "runAfter": {
    "Compose_catch_try_result": [
      "Succeeded"
    ]
  }
},
"Select_catch_error_details": {
  "type": "Select",
  "inputs": {
    "from": "@body('Filter_catch_failed_actions')",
    "select": {
      "action": "@item()?['name']",
      "status": "@item()?['status']",
      "code": "@coalesce(item()?['error']?['code'], item()?['code'], item()?['outputs']?['statusCode'], '')",
      "message": "@coalesce(item()?['error']?['message'], item()?['outputs']?['body']?['error']?['message'], item()?['outputs']?['body']?['message'], '')",
      "startTime": "@item()?['startTime']",
      "endTime": "@item()?['endTime']",
      "trackingId": "@coalesce(item()?['trackingId'], item()?['clientTrackingId'], '')"
    }
  },
  "runAfter": {
    "Filter_catch_failed_actions": [
      "Succeeded"
    ]
  }
},
"Compose_catch_log_payload": {
  "type": "Compose",
  "inputs": {
    "flowName": "@coalesce(workflow()?['tags']?['flowDisplayName'], workflow()?['name'])",
    "environment": "@coalesce(workflow()?['tags']?['environmentName'], '')",
    "runName": "@workflow()?['run']?['name']",
    "runId": "@workflow()?['run']?['id']",
    "loggedAtUtc": "@utcNow()",
    "businessKey": "@variables('varLogBusinessKey')",
    "sourceItemId": "@variables('varLogSourceItemId')",
    "sourceFileName": "@variables('varLogSourceFileName')",
    "failedActions": "@body('Select_catch_error_details')",
    "rawTryResultExcerpt": "@take(string(outputs('Compose_catch_try_result')), 4000)"
  },
  "runAfter": {
    "Select_catch_error_details": [
      "Succeeded"
    ]
  }
}
```

Create the `varLogBusinessKey`, `varLogSourceItemId`, and `varLogSourceFileName` variables before `TRY_<domain>` starts. Do not build CATCH context from outputs of actions that may have failed.

If the TRY scope contains nested scopes, `result('TRY_<domain>')` may only surface the nested scope result. Add similar `result('<Nested_scope_name>')` logging for nested scopes whose inner action names matter.

## Email Summary Expression

Use this in the body of a mail action after `Compose_catch_log_payload`. Do not include `outputs('Compose_catch_try_result')` in email by default.

```text
concat(
  '<h2>Power Automate flow failed</h2>',
  '<p><b>Flow:</b> ', coalesce(workflow()?['tags']?['flowDisplayName'], workflow()?['name']), '</p>',
  '<p><b>Environment:</b> ', coalesce(workflow()?['tags']?['environmentName'], ''), '</p>',
  '<p><b>Run:</b> ', workflow()?['run']?['name'], '</p>',
  '<p><b>Business key:</b> ', variables('varLogBusinessKey'), '</p>',
  '<p><b>Source item:</b> ', variables('varLogSourceItemId'), '</p>',
  '<p><b>Source file:</b> ', variables('varLogSourceFileName'), '</p>',
  '<h3>Error details</h3>',
  '<pre>',
  replace(
    replace(
      replace(string(body('Select_catch_error_details')), '&', '&amp;'),
      '<',
      '&lt;'
    ),
    '>',
    '&gt;'
  ),
  '</pre>'
)
```

## Fail The Flow After Logging

Add a `Terminate_Failed` action after the final approved log or alert action unless the user explicitly wants the flow run to succeed after CATCH. If `Compose_catch_log_payload` is the final catch action, use this shape:

```json
"Terminate_Failed": {
  "type": "Terminate",
  "inputs": {
    "runStatus": "Failed",
    "runError": {
      "code": "FLOW_BUSINESS_ERROR",
      "message": "Business processing failed. See structured log payload."
    }
  },
  "runAfter": {
    "Compose_catch_log_payload": [
      "Succeeded"
    ]
  }
}
```

If an email or log-store action follows `Compose_catch_log_payload`, make `Terminate_Failed` run after that final action. Decide deliberately whether `Terminate_Failed` should also run after log/alert failure or timeout.

## Validation Checklist

- Force one controlled failure and verify the catch scope runs.
- Confirm the email or log record contains at least one failed action with message and tracking ID when available.
- Confirm the catch path still runs if the failed action has no `error.message`.
- Confirm email excludes raw TRY results unless an approved exception exists.
- Confirm payload size is acceptable for the selected log destination.
- Confirm the flow run terminates as `Failed` after CATCH unless success-after-catch was explicitly requested.
