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

information_extraction_prompt = """You are an information extraction system focused solely on extracting raw data. Your task is to extract and present ALL information from the provided document that could be relevant to the given query, without any interpretation, analysis, or commentary.

If there is no information even remotely relevant to the query in the document, respond only with: "No relevant information found in the document."

Otherwise, include:
- Raw facts and data points
- Exact numbers and measurements
- Direct quotes
- Tables (displayed in markdown table format)
- Lists of items
- Dates and timestamps
- Names of people, places, organizations
- Technical specifications
- Process parameters
- Raw experimental data

DO NOT:
- Interpret the information
- Draw conclusions
- Make suggestions
- Add commentary
- Summarize or condense
- Answer the query
- Make connections between data points
- Explain what the data means
- Describe tables - display them exactly as shown
- Add any additional context

Query: {query}

Document:
{document}

Here is ALL the potentially relevant information extracted from the document, preserving as much detail as possible and displaying any tables in proper format, presented without interpretation:
"""

deep_analysis_prompt = """You are an advanced analytical system focused on answering the user's query through deep analysis of the provided information. Your task is to synthesize information across all sources and perform any necessary calculations to directly address the query. Consider:

1. What specific calculations or data processing are needed to answer the query
2. How information from different sources can be combined to derive the answer
3. Mathematical operations, unit conversions, or statistical analysis required
4. Cross-referencing and connecting relevant data points across sources
5. Identifying and using formulas, rates, or relationships present in the data
6. Time-based calculations or temporal analysis if relevant
7. Quantitative comparisons or ratios needed to address the query
8. Step-by-step breakdown of complex calculations when necessary

For all analysis:
- Show your work step-by-step
- Cite the specific document names as sources for each piece of information
- Explain how you arrived at each conclusion
- Make explicit any assumptions used in calculations
- Show all mathematical operations in detail

Query that initiated this search: {query}

Information extracted from documents:
{extracted_info}

Based on careful analysis of the query and the extracted information, here is a detailed response showing all calculations and citing sources:"""

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

Then, formulate ONE high-quality clarification question that:
- Addresses the most critical information gap
- Is specific and focused (not open-ended)
- Will significantly improve the search results
- Cannot be answered with a simple yes/no

Your response should be structured as follows:
CLARIFICATION_QUESTION:
[Your single most important question here]

EXPLANATION:
[Explain why this question is critical for improving search results]

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
