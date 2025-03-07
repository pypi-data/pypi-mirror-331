from typing import List, Optional

from pydantic import BaseModel

from .types import TaskCall


class CodeContextItem(BaseModel):
    content: str
    type: Optional[str] = None
    filepath: Optional[str] = None


class CodeContext(BaseModel):
    items: List[CodeContextItem]


class CodeTaskAttributes(BaseModel):
    prefix: str
    suffix: Optional[str] = None
    filepath: Optional[str] = None
    context: Optional[CodeContext] = None
    useControl: Optional[bool] = None
    provideGenerationDetails: Optional[bool] = None


# One-line


class CodeOneLineAllCompleteTask:
    """One-line code completion task for any language."""

    name = "code-one-line-all-complete"

    @classmethod
    def default(
        cls,
        prefix: str,
        suffix: Optional[str] = None,
        filepath: Optional[str] = None,
        context: Optional[CodeContext] = None,
        use_control: Optional[bool] = None,
        provide_generation_details: Optional[bool] = None,
    ) -> TaskCall:
        """
        Args:
            prefix: Code before cursor
            suffix: Code after cursor
            filepath: Relative path of the file, where completion is requested, with filename and extension
            context: Gathered context for code completion
            use_control: Whether to use control model or not
            provide_generation_details: Include logits from filter model in response
        """
        return TaskCall(
            id=f"{cls.name}:default",
            parameters=CodeTaskAttributes(
                prefix=prefix,
                suffix=suffix,
                filepath=filepath,
                context=context,
                useControl=use_control,
                provideGenerationDetails=provide_generation_details,
            ),
        )


class CodeOneLineKotlinCompleteTask(CodeOneLineAllCompleteTask):
    """One-line code completion task for Kotlin."""

    name = "code-one-line-kt-complete"


class CodeOneLinePythonJetCompleteTask(CodeOneLineAllCompleteTask):
    """One-line code completion task for Python."""

    name = "code-one-line-python-jet-complete"


# Multi-line


class CodeMultiLineAllCompleteTask:
    """Multi-line code completion task for all languages."""

    name = "code-multi-line-all-complete"

    @classmethod
    def fast(cls, prefix: str, suffix: str) -> TaskCall:
        """
        Args:
            prefix: Code before cursor
            suffix: Code after cursor
        """
        return TaskCall(
            id=f"{cls.name}:fast",
            parameters=dict(prefix=prefix, suffix=suffix),
        )

    @classmethod
    def slow(cls, prefix: str, suffix: str) -> TaskCall:
        """
        Args:
            prefix: Code before cursor
            suffix: Code after cursor
        """
        return TaskCall(
            id=f"{cls.name}:slow",
            parameters=dict(prefix=prefix, suffix=suffix),
        )


class CodeMultiLineJetKotlinCompleteTask(CodeOneLineAllCompleteTask):
    """Multi-line code completion task for Kotlin."""

    name = "code-multi-line-jet-kotlin-complete"


class CodeMultiLineJetPythonCompleteTask(CodeOneLineAllCompleteTask):
    """Multi-line code completion task for Python."""

    name = "code-multi-line-jet-python-complete"
