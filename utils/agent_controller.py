from utils.agent_schema import AgentDecision
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

def agent_controller(message: str) -> AgentDecision:
    """
    LLM-based agent decision maker.
    Raises exception if LLM is unavailable (handled by caller).
    """
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    parser = PydanticOutputParser(pydantic_object=AgentDecision)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are an AI controller for a resort system.
Decide which agent should handle the user request.

Agents:
- receptionist: general info, facilities, availability
- restaurant: food ordering, menu, billing
- room_service: cleaning, laundry, amenities
- checkout: checkout request

Return ONLY structured output.
{format_instructions}
"""),
        ("human", "{message}")
    ])

    chain = prompt | llm | parser

    return chain.invoke({
        "message": message,
        "format_instructions": parser.get_format_instructions()
    })
