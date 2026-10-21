---
name: groq-evaluation
description: Evaluate a written student answer with Groq via LangChain ChatGroq and validate the structured JSON response.
---

# groq-evaluation

1. Build a prompt from the question text, total marks, rubric/sample answer, and extracted student answer.
2. Call `langchain-groq` `ChatGroq(model=settings.GROQ_MODEL)` with a system message requiring valid JSON only.
3. Parse the response as JSON; validate required keys (`score`, `justification`, `strengths`, `lackings`, `suggestions`) and that `score` is a number between 0 and `marks`.
4. On validation failure, retry once; if it still fails, flag the answer for manual grading.
5. Store only the AI draft fields in `Answers`; never expose them to student routes until `is_approved` is true.
