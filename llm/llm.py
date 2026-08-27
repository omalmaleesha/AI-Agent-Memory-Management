from types import SimpleNamespace
from typing import Any, Type
from groq import AuthenticationError
from langchain_groq import ChatGroq
from config.settings import settings
import json
from llm.fallbacks.memory_router_fallback import (
    MemoryRouterFallback,
)

from llm.fallbacks.memory_extractor_fallback import (
    MemoryExtractorFallback,
)

class LLMService:
    def __init__(self):
        self.available = bool(settings.GROQ_API_KEY)
        if not self.available:
            self.model = None
            return
        self.model = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.2,
        )
        self.memory_router_fallback = (
            MemoryRouterFallback()
        )

        self.memory_extractor_fallback = (
            MemoryExtractorFallback()
        )

    # PROMPT HELPERS
    def _extract_section(self,prompt: str,marker: str,) -> str:
        if marker not in prompt:
            return ""
        section = prompt.split(marker, 1)[1]
        if "\n\n" in section:
            section = section.split("\n\n", 1)[0]
        return section.strip()

    # FALLBACK RESPONSE
    def _generate_fallback_response(self,prompt: str,) -> str:
        user_request = self._extract_section(
            prompt,
            "USER REQUEST:",
        )
        context = self._extract_section(
            prompt,
            "MEMORY CONTEXT:",
        )
        user_request = user_request.strip()
        context = context.strip()

        if context:
            return (
                "I could not reach Groq just now, "
                "so I am using the available memory context.\n\n"
                f"Request: {user_request}\n\n"
                f"Context: {context}"
            ).strip()

        if user_request:
            return (
                "I could not reach Groq just now, "
                "so I am responding with a local fallback.\n\n"
                f"You asked: {user_request}"
            )

        return (
            "I could not reach Groq just now, "
            "so I am responding with a local fallback."
        )

    # FALLBACK MESSAGE
    def _fallback_message(self,prompt: str,) -> SimpleNamespace:
        return SimpleNamespace(
            content=self._generate_fallback_response(prompt)
        )

    # FALLBACK STRUCTURED OUTPUT
    def _fallback_structured_output(self,schema: Type,prompt: str,):
        schema_name = getattr(
            schema,
            "__name__",
            "",
        )
        # MEMORY ROUTING
        if schema_name == "MemoryRouting":

            user_request = self._extract_section(
                prompt,
                "User request:",
            )

            if not user_request:
                user_request = self._extract_section(
                    prompt,
                    "USER REQUEST:",
                )

            payload = {
                "required_memories": self._route_memories(
                    user_request
                )
            }

        # MEMORY EXTRACTION
        elif schema_name == "MemoryExtraction":

            payload = self._extract_memories(
                prompt
            )

        # UNKNOWN SCHEMA

        else:
            payload = {}

        try:
            return schema(**payload)

        except Exception:

            if hasattr(
                schema,
                "model_validate",
            ):
                return schema.model_validate(
                    payload
                )

            raise

    # GET MODEL

    def get_model(self) -> ChatGroq | None:
        """
        Return the underlying LangChain ChatGroq model.
        """

        return self.model

    # NORMAL INVOKE

    def invoke(
        self,
        prompt: str,
        response_format: Any = None,
        **kwargs,
    ):
        """
        Invoke the LLM.

        Supported:

            llm.invoke(prompt)

        JSON mode:

            llm.invoke(
                prompt,
                response_format={"type": "json_object"}
            )

        Structured schema:

            llm.invoke(
                prompt,
                response_format=SomePydanticModel
            )
        """
        # NO MODEL / NO API KEY

        if not self.available or self.model is None:

            if response_format is not None:

                # JSON mode does not have a schema to validate
                if isinstance(response_format, dict):
                    return SimpleNamespace(
                        content=json.dumps(
                            {
                                "required_memories": []
                            }
                        )
                    )

                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

            return self._fallback_message(prompt)
        # GROQ JSON MODE
        if isinstance(response_format, dict):

            try:

                response = self.model.invoke(
                    prompt,
                    response_format=response_format,
                    **kwargs,
                )

                return response

            except AuthenticationError:

                print(
                    "[LLM SERVICE] Groq authentication failed."
                )

                return SimpleNamespace(
                    content=json.dumps(
                        {
                            "required_memories": []
                        }
                    )
                )

            except Exception as exc:

                print(
                    "[LLM SERVICE] JSON invocation failed:",
                    type(exc).__name__,
                    str(exc),
                )

                return SimpleNamespace(
                    content=json.dumps(
                        {
                            "required_memories": []
                        }
                    )
                )

        # PYDANTIC STRUCTURED OUTPUT
        if response_format is not None:

            try:

                structured_model = (
                    self.model.with_structured_output(
                        response_format
                    )
                )

                return structured_model.invoke(
                    prompt,
                    **kwargs,
                )

            except AuthenticationError:

                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

            except Exception as exc:

                print(
                    "[LLM SERVICE] Structured invocation failed:",
                    type(exc).__name__,
                    str(exc),
                )

                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

        # NORMAL TEXT OUTPUT
        try:

            return self.model.invoke(
                prompt,
                **kwargs,
            )

        except AuthenticationError:

            print(
                "[LLM SERVICE] Groq authentication failed."
            )

            return self._fallback_message(prompt)

        except Exception as exc:

            print(
                "[LLM SERVICE] LLM invocation failed:",
                type(exc).__name__,
                str(exc),
            )

            return self._fallback_message(prompt)

    # ASYNC INVOKE
    async def ainvoke(
        self,
        prompt: str,
        response_format: Any = None,
        **kwargs,
    ):
        """
        Async equivalent of invoke().
        """
        if not self.available or self.model is None:

            if response_format is not None:
                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

            return self._fallback_message(
                prompt
            )

        if response_format is not None:

            try:

                structured_model = (
                    self.model.with_structured_output(
                        response_format
                    )
                )

                return await structured_model.ainvoke(
                    prompt,
                    **kwargs,
                )

            except AuthenticationError:

                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

            except Exception as exc:

                print(
                    "[LLM SERVICE] Async structured invocation failed:",
                    type(exc).__name__,
                    str(exc),
                )

                return self._fallback_structured_output(
                    response_format,
                    prompt,
                )

        try:

            return await self.model.ainvoke(
                prompt,
                **kwargs,
            )

        except AuthenticationError:

            print(
                "[LLM SERVICE] Groq authentication failed."
            )

            return self._fallback_message(
                prompt
            )

        except Exception as exc:

            print(
                "[LLM SERVICE] Async invocation failed:",
                type(exc).__name__,
                str(exc),
            )

            return self._fallback_message(
                prompt
            )

    # STRUCTURED OUTPUT
    def with_structured_output(self,schema: Type,):
        """
        Create a structured-output LLM wrapper.

        Example:

            llm = LLMService()

            router = llm.with_structured_output(
                MemoryRouting
            )

            result = router.invoke(prompt)
        """
        # NO API KEY
        if not self.available or self.model is None:
            parent = self

            class StructuredLLMWrapper:
                def __init__(self):
                    self.output_schema = schema
                def invoke(self,prompt: str,**kwargs,):
                    return parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

                async def ainvoke(self,prompt: str,**kwargs,):
                    return parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

            return StructuredLLMWrapper()

        # CREATE STRUCTURED MODEL
        try:
            structured_model = (
                self.model.with_structured_output(
                    schema
                )
            )

        except Exception as exc:
            print(
                "[LLM SERVICE] Could not create structured model:",
                type(exc).__name__,
                str(exc),
            )
            structured_model = None

        # WRAPPER
        class StructuredLLMWrapper:
            def __init__(
                self,
                parent,
                runnable,
                output_schema,
            ):
                self.parent = parent
                self.runnable = runnable
                self.output_schema = output_schema

            def invoke(self,prompt: str,**kwargs,):
                if self.runnable is None:
                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

                try:
                    return self.runnable.invoke(
                        prompt,
                        **kwargs,
                    )

                except AuthenticationError:
                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

                except Exception as exc:
                    print(
                        "[LLM SERVICE] Structured output failed:",
                        type(exc).__name__,
                        str(exc),
                    )

                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

            async def ainvoke(self,prompt: str,**kwargs,):
                if self.runnable is None:
                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

                try:
                    return await self.runnable.ainvoke(
                        prompt,
                        **kwargs,
                    )

                except AuthenticationError:
                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

                except Exception as exc:
                    print(
                        "[LLM SERVICE] Async structured output failed:",
                        type(exc).__name__,
                        str(exc),
                    )

                    return self.parent._fallback_structured_output(
                        self.output_schema,
                        prompt,
                    )

        return StructuredLLMWrapper(
            self,
            structured_model,
            schema,
        )

# SINGLETON
llm_service = LLMService()