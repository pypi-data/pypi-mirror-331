import os
from openai import OpenAI
from src.commons.utils import get_model_server_logger
from src.core.guardrails import get_guardrail_handler
from src.core.function_calling import (
    ArchIntentConfig,
    ArchIntentHandler,
    ArchFunctionConfig,
    ArchFunctionHandler,
)


# Define logger
logger = get_model_server_logger()


# Define the client
ARCH_ENDPOINT = os.getenv("ARCH_ENDPOINT", "https://archfc.katanemo.dev/v1")
ARCH_API_KEY = "EMPTY"
ARCH_CLIENT = OpenAI(base_url=ARCH_ENDPOINT, api_key=ARCH_API_KEY)

# Define model names
ARCH_INTENT_MODEL_ALIAS = "Arch-Intent"
ARCH_FUNCTION_MODEL_ALIAS = "Arch-Function"
ARCH_GUARD_MODEL_ALIAS = "katanemo/Arch-Guard"

# Define model handlers
handler_map = {
    "Arch-Intent": ArchIntentHandler(
        ARCH_CLIENT, ARCH_INTENT_MODEL_ALIAS, ArchIntentConfig
    ),
    "Arch-Function": ArchFunctionHandler(
        ARCH_CLIENT, ARCH_FUNCTION_MODEL_ALIAS, ArchFunctionConfig
    ),
    "Arch-Guard": get_guardrail_handler(ARCH_GUARD_MODEL_ALIAS),
}
