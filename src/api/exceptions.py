class APIError(Exception):
    """Raised when the remote API returns an error response."""
    def __init__(self, step: str, table: str, message: str, status_code: int = None, body: str = None):
        self.step        = step
        self.table       = table
        self.status_code = status_code
        self.body        = body
        # Pull the human-readable cause out of the upstream JSON envelope so callers
        # get a precise reason (e.g. "field X does not exist in the schema") instead
        # of a raw response blob.
        self.reason      = self._extract_reason(body) or message
        detail = f"[{step} → {table}] {message}"
        if status_code:
            detail += f"  (HTTP {status_code})"
        if self.reason and self.reason != message:
            detail += f"\n  Reason: {self.reason}"
        if body:
            detail += f"\n  Response body: {body}"
        super().__init__(detail)

    @staticmethod
    def _extract_reason(body):
        """Best-effort extraction of error.details / message from the API body."""
        if not body:
            return None
        try:
            import json
            data = json.loads(body) if isinstance(body, str) else body
        except (ValueError, TypeError):
            return None
        if not isinstance(data, dict):
            return None
        err = data.get("error")
        if isinstance(err, dict):
            # `details` is the most specific (field-level) message; fall back to exception/message
            return err.get("details") or err.get("exception") or err.get("message")
        return data.get("message")


class LookupError(Exception):
    """Raised when a required master-data record is not found."""
    def __init__(self, table: str, field: str, value: str):
        self.table = table
        self.field = field
        self.value = value
        super().__init__(
            f"[Lookup] '{value}' not found in {table}.{field}. "
            f"Ensure master data is seeded before running the pipeline."
        )


class ValidationError(Exception):
    """Raised when invoice input data is missing required fields."""
    def __init__(self, field_path: str, reason: str = "is required"):
        self.field_path = field_path
        super().__init__(f"[Validation] invoice_data.{field_path} {reason}")
