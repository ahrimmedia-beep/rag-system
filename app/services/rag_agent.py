from app.domain.llm import LLMProvider
from app.domain.models import Answer, Message
from app.services.generation import GenerationService
from app.services.memory import MemoryService
from app.services.retrieval import RetrievalService

AGENT_PROMPT = (
    "You are a support assistant for a cryptocurrency exchange. When a question needs "
    "help-center information, call the `search_knowledge_base` tool with a focused query. "
    "For pure greetings or small talk, answer directly without the tool."
)

SEARCH_TOOL: dict[str, object] = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": (
            "Search the exchange help-center knowledge base for articles relevant to the "
            "question."
        ),
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Focused search query"}},
            "required": ["query"],
        },
    },
}


class RagAgentService:
    def __init__(
        self,
        llm: LLMProvider,
        retrieval: RetrievalService,
        generation: GenerationService,
        memory: MemoryService,
        agent_prompt: str = AGENT_PROMPT,
    ) -> None:
        self._llm = llm
        self._retrieval = retrieval
        self._generation = generation
        self._memory = memory
        self._agent_prompt = agent_prompt

    def answer(self, session_id: str, question: str) -> Answer:
        history = self._memory.get(session_id)
        messages = [*history, Message(role="user", content=question)]
        decision = self._llm.chat(self._agent_prompt, messages, tools=[SEARCH_TOOL])

        tool_call = next(
            (tc for tc in decision.tool_calls if tc.name == "search_knowledge_base"), None
        )
        if tool_call is None:
            answer = Answer(answer=decision.content or "", sources=[])
        else:
            query = str(tool_call.arguments.get("query") or question)
            retrieved = self._retrieval.retrieve(query)
            answer = self._generation.generate(question, retrieved, history)

        self._memory.append(session_id, question, answer.answer)
        return answer
