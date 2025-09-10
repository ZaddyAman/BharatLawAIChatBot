import asyncio
from query_engine import query_legal_assistant

async def main():
    question = "What does Section 246 of IPC state?"
    response = await query_legal_assistant(question)

    print("\n🧠 AI Legal Assistant:\n", response)

if __name__ == "__main__":
    asyncio.run(main())
