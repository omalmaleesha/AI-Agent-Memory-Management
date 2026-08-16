from langchain_groq import ChatGroq

from config.settings import settings


class LLMService:

    def __init__(self):
        self.model = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.2,
        )

    def get_model(self) -> ChatGroq:
        """
        Return the underlying LangChain ChatGroq model.

        This allows nodes to use methods such as:
        - invoke()
        - ainvoke()
        - with_structured_output()
        """
        return self.model

    def invoke(self, prompt: str):
        """
        Simple LLM invocation.
        """
        return self.model.invoke(prompt)

    def with_structured_output(self, schema):
        """
        Create a structured-output LLM.

        Example:
            llm.with_structured_output(MemoryRouting)
        """
        return self.model.with_structured_output(schema)


llm_service = LLMService()