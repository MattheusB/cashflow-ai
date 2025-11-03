"""LLM service for expense extraction using LangChain."""

import json
from typing import Any

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..schemas import ExpenseCategory, ExpenseExtraction
from ..utils.config import get_settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMService:
    """Service for processing messages with LLM to extract expense information."""

    def __init__(self) -> None:
        """Initialize LLM service with configured provider."""
        self.settings = get_settings()
        self.llm = self._initialize_llm()
        self.parser = PydanticOutputParser(pydantic_object=ExpenseExtraction)
        self.prompt = self._create_prompt()
        logger.info(f"LLM Service initialized with model: {self.settings.llm_model}")

    def _initialize_llm(self) -> ChatOpenAI | ChatAnthropic:
        """Initialize the appropriate LLM based on configuration."""
        provider = self.settings.get_llm_provider()

        if provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is required but not configured")
            return ChatOpenAI(
                model=self.settings.llm_model,
                api_key=self.settings.openai_api_key,
                temperature=0.0,
            )
        elif provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError("Anthropic API key is required but not configured")
            return ChatAnthropic(
                model=self.settings.llm_model,
                api_key=self.settings.anthropic_api_key,
                temperature=0.0,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_prompt(self) -> PromptTemplate:
        """Create the prompt template for expense extraction."""
        categories_list = ", ".join([cat.value for cat in ExpenseCategory])

        template = """You are an AI assistant specialized in analyzing messages to determine if they represent expenses and extracting relevant information.

Your task is to analyze the following message and determine:
1. Is this message describing an expense? (not greetings, questions, or random chat)
2. If yes, extract: description, amount, and category

Valid categories: {categories}

Rules:
- Only mark as expense if there's a clear description and amount
- Ignore greetings like "hi", "hello", "bom dia", "oi", etc.
- Ignore questions or commands
- Amount should be a positive number
- If currency is mentioned (reais, R$, dollars, $), extract just the number
- Choose the most appropriate category from the list above
- If unclear, use "Other" as category

Message to analyze: {message}

{format_instructions}

Return valid JSON only, no additional text."""

        return PromptTemplate(
            template=template,
            input_variables=["message"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "categories": categories_list,
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def extract_expense(self, message: str) -> ExpenseExtraction:
        """
        Extract expense information from a message using LLM with retry mechanism.

        Args:
            message: User message to analyze

        Returns:
            ExpenseExtraction: Parsed expense information

        Raises:
            Exception: If LLM processing fails after retries
        """
        try:
            logger.info(f"Processing message: {message[:50]}...")

            chain = self.prompt | self.llm

            response = await chain.ainvoke({"message": message})

            response_text = response.content if hasattr(response, "content") else str(response)

            logger.debug(f"LLM raw response: {response_text}")

            try:
                parsed_data = self.parser.parse(response_text)
            except Exception as parse_error:
                logger.warning(f"Initial parsing failed: {parse_error}, attempting cleanup...")
                parsed_data = self._extract_and_parse_json(response_text)

            logger.info(
                f"Extraction result: is_expense={parsed_data.is_expense}, "
                f"category={parsed_data.category}, amount={parsed_data.amount}"
            )

            return parsed_data

        except Exception as e:
            logger.error(f"Error extracting expense: {e}", exc_info=True)
            raise

    def _extract_and_parse_json(self, text: str) -> ExpenseExtraction:
        """Extract and parse JSON from text that might contain additional content."""
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")

        json_str = text[start_idx:end_idx]
        data = json.loads(json_str)

        return ExpenseExtraction(**data)

    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        try:
            provider = self.settings.get_llm_provider()
            if provider == "openai":
                return bool(self.settings.openai_api_key)
            elif provider == "anthropic":
                return bool(self.settings.anthropic_api_key)
            return False
        except Exception:
            return False
