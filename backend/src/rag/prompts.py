"""All LLM prompt templates for the Legal Document Analyzer."""

DOC_TYPE_PROMPT = """You are a legal document classifier. Given the first section of a document, \
identify its type. Respond with ONLY a JSON object, no markdown.

Document types: contract, nda, lease, employment, terms_of_service, \
privacy_policy, other

Document excerpt:
{text}

Respond with:
{{"doc_type": "<type>", "confidence": "<high|medium|low>", "reasoning": "<one sentence>"}}"""


CLAUSE_EXTRACTION_PROMPT = """You are a senior legal analyst. Extract all notable clauses from the following \
legal document text. For each clause, identify its type, copy the verbatim text, \
and write a plain-English summary.

Clause types to identify:
- liability_limitation, indemnification, intellectual_property, termination,
  confidentiality, payment_terms, governing_law, dispute_resolution,
  force_majeure, non_compete, data_privacy, warranty

Document text:
{text}

Respond ONLY with a valid JSON array. No markdown, no preamble.
[
  {{
    "clause_type": "<type>",
    "verbatim_text": "<exact text from document>",
    "section_reference": "<e.g. Section 8.2 or null>",
    "plain_english": "<1-2 sentence plain English summary>"
  }}
]"""


RISK_SCORING_PROMPT = """You are a legal risk analyst. Given the following extracted clauses, assess the \
risk level of each clause and compute an overall document risk score.

Risk levels: critical (severe legal exposure), high (above-market risk), \
medium (notable but manageable), low (standard terms), info (neutral / informational)

Clauses:
{clauses_json}

Respond ONLY with valid JSON. No markdown.
{{
  "risk_score": <0-100>,
  "scored_clauses": [
    {{
      "clause_type": "<type>",
      "risk_level": "<level>",
      "risk_reason": "<one sentence explaining the risk>"
    }}
  ],
  "overall_risk_summary": "<2-3 sentences>"
}}"""


ANOMALY_DETECTION_PROMPT = """You are a contract review specialist. Given the following document analysis, \
identify any missing standard clauses or unusual provisions.

Document type: {doc_type}
Extracted clause types: {clause_types_found}
Document text sample: {text_sample}

Common clauses expected for {doc_type}:
{expected_clauses}

Respond ONLY with valid JSON.
{{
  "anomalies": [
    {{
      "anomaly_type": "missing_clause | unusual_provision | one_sided_language",
      "description": "<clear explanation>",
      "severity": "critical | warning"
    }}
  ]
}}"""


SUMMARY_PROMPT = """You are a legal analyst writing for a business executive with no legal background.
Summarize the following legal document at three levels of detail.

Document type: {doc_type}
Parties: {parties}

Document text:
{text}

Respond ONLY with valid JSON.
{{
  "brief": "<2-3 sentences, plain language, suitable for a non-lawyer>",
  "standard": "<one paragraph per major section of the document>",
  "detailed": "<comprehensive structured summary covering all key terms, \
                obligations, rights, and conditions>"
}}"""


RAG_SYSTEM_PROMPT = """You are a legal document assistant. Answer questions about the provided legal \
document using ONLY the context below. If the answer is not in the context, \
say so clearly. Do not hallucinate. Always cite which section your answer \
comes from.

Context from document:
{context}"""


# Expected clauses by document type (for anomaly detection)
EXPECTED_CLAUSES = {
    "contract": [
        "governing_law", "termination", "liability_limitation",
        "confidentiality", "payment_terms", "dispute_resolution",
        "indemnification", "warranty",
    ],
    "nda": [
        "confidentiality", "termination", "governing_law",
        "dispute_resolution", "liability_limitation",
    ],
    "lease": [
        "termination", "payment_terms", "governing_law",
        "liability_limitation", "dispute_resolution",
    ],
    "employment": [
        "termination", "confidentiality", "non_compete",
        "intellectual_property", "governing_law", "payment_terms",
    ],
    "terms_of_service": [
        "governing_law", "liability_limitation", "termination",
        "data_privacy", "dispute_resolution", "warranty",
    ],
    "privacy_policy": [
        "data_privacy", "governing_law",
    ],
    "other": [
        "governing_law", "termination", "liability_limitation",
    ],
}
