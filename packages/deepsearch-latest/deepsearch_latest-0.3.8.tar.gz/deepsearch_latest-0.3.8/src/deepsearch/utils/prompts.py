# Define your prompts
document_summary_prompt = """
You are a librarian that stores documents in a database for a company called Digestiva. The company produces an enzyme produce and is engaged in both research as well as production. 
Given a document titled '{document_name}', you need to think deeply about the document and then create a description of the document that can be used to retrieve the document at a later time.
Do not return anything expect for the description of the document. The description should include all key information about the document such that if someone was searching for a small piece of information that is included within the document, they would be able to know that this document contains that information. Pay special attention to including any names of people, companies, organizations, and any dates mentioned in the document.

Here is the document:
{document}

Here is a description of the document focused on capturing the key information that would allow someone to retrieve this document if they were searching for specific details contained within it, including all names of people, companies, organizations and dates:
"""

pdf_transcription_prompt = "Transcribe all text from this pdf page exactly as written, with no introduction or commentary. For any unclear or uncertain text, use {probably - description} format in place of the text."

information_extraction_prompt = """You are an information extraction system focused on preserving original document content. Your task is to copy the exact text from the provided document that could be relevant to the given query, maintaining the original wording, formatting, and structure.

If there is no information even remotely relevant to the query in the document, respond only with: "No relevant information found in the document."

Otherwise:
- Copy the exact text from the document that might be relevant
- Preserve original wording, punctuation, and formatting
- Maintain the original structure (paragraphs, bullet points, etc.)
- Include all tables exactly as they appear (displayed in markdown table format)
- Keep all numerical data, dates, and measurements exactly as written
- Preserve all names, technical terms, and specialized vocabulary

DO NOT:
- Interpret the information
- Summarize or paraphrase
- Add commentary
- Answer the query
- Make connections between data points
- Explain what the data means
- Modify tables in any way
- Reformat or restructure the content

Query: {query}

Document:
{document}

Here is the relevant information from the document, preserved exactly as written:

[COPY RELEVANT CONTENT HERE]

EXCLUDED CONTENT:
[Briefly explain what types of information were excluded and why they were deemed irrelevant to the query. Be specific about the nature of the excluded content.]
"""

clarification_assessment_prompt = """You are an assistant helping to refine a search query. Based on the user's query and available source summaries, formulate a single, high-quality clarification question before performing the search.

User's query: {query}

Available source summaries:
{summaries}

Conversation history:
{conversation_history}

First, analyze the query, conversation history, and available sources to identify:
1. The most critical ambiguity or missing detail in the query
2. The most significant gap in information needed to provide relevant results
3. The single most important clarification that would improve search results
4. The most relevant source documents that inform your clarification question

Then, formulate ONE high-quality clarification question that:
- Addresses the most critical information gap
- Is specific and focused (not open-ended)
- Will significantly improve the search results
- Cannot be answered with a simple yes/no
- References specific source documents when appropriate

Your response should be structured as follows:
CLARIFICATION_QUESTION:
[Your single most important question here]

EXPLANATION:
[Explain why this question is critical for improving search results]

RELEVANT_SOURCES:
[List the names of 3-5 most relevant source documents that informed your question]

POTENTIAL_REFINED_QUERY:
[Suggest how the query might be refined after receiving an answer to your question]"""

search_refinement_prompt = """You are a search specialist helping to refine a search query based on user feedback. Your goal is to adjust the search to better match what the user is looking for.

Original query: {query}

Current search results:
{search_results}

Conversation history:
{conversation_history}

User feedback:
{user_feedback}

Based on the user's feedback and conversation history, determine how to adjust the search:
1. Identify which sources the user wants to keep or remove
2. Understand what additional information the user is looking for
3. Determine how to modify the query to better match the user's needs

Your response should be structured as follows:
REFINED_QUERY:
[Provide a refined search query based on user feedback]

EXPLANATION:
[Explain how this refined query addresses the user's feedback]

SOURCES_TO_INCLUDE:
[List any specific sources the user wants to include, or "all" if not specified]

SOURCES_TO_EXCLUDE:
[List any specific sources the user wants to exclude, or "none" if not specified]"""

final_answer_prompt = """You are an assistant providing a comprehensive answer based on search results. Your task is to synthesize the information from the search results to directly answer the user's query.

User's query: {query}

Conversation history:
{conversation_history}

Search results:
{search_results}

Provide a comprehensive answer that:
1. Directly addresses the user's query
2. Synthesizes information from all relevant sources
3. Cites specific sources for key information
4. Is well-structured and easy to understand
5. Acknowledges any limitations or gaps in the available information

Your answer:"""
