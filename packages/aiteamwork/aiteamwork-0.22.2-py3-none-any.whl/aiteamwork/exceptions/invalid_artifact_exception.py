from aiteamwork.exceptions.llm_runtime_exception import LLMRuntimeException


class InvalidArtifactException(LLMRuntimeException):
    issues: list[str]

    def __init__(self, issues: list[str], *args):
        super().__init__(*args)
        self.issues = issues
