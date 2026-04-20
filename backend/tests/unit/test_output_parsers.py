import pytest
from pydantic import ValidationError

from src.rag.output_parsers import (
    DocTypeResult,
    ExtractedClause,
    RiskScoringResult,
    parse_llm_json,
    parse_llm_json_list,
)


class TestParseLlmJson:
    def test_valid_json(self):
        raw = '{"doc_type": "contract", "confidence": "high", "reasoning": "Contains terms"}'
        result = parse_llm_json(raw, DocTypeResult)
        assert result.doc_type == "contract"
        assert result.confidence == "high"

    def test_json_with_markdown_fences(self):
        raw = '```json\n{"doc_type": "nda", "confidence": "medium", "reasoning": "NDA language"}\n```'
        result = parse_llm_json(raw, DocTypeResult)
        assert result.doc_type == "nda"

    def test_json_with_plain_fences(self):
        raw = '```\n{"doc_type": "lease", "confidence": "low", "reasoning": "Lease terms"}\n```'
        result = parse_llm_json(raw, DocTypeResult)
        assert result.doc_type == "lease"

    def test_invalid_json_raises_value_error(self):
        raw = "This is not JSON at all"
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_llm_json(raw, DocTypeResult)

    def test_missing_required_field_raises_validation_error(self):
        raw = '{"doc_type": "contract"}'  # missing confidence and reasoning
        with pytest.raises(ValidationError):
            parse_llm_json(raw, DocTypeResult)


class TestParseLlmJsonList:
    def test_valid_list(self):
        raw = '[{"clause_type": "liability", "verbatim_text": "In no event..."}]'
        result = parse_llm_json_list(raw, ExtractedClause)
        assert len(result) == 1
        assert result[0].clause_type == "liability"

    def test_empty_list(self):
        raw = "[]"
        result = parse_llm_json_list(raw, ExtractedClause)
        assert result == []

    def test_not_a_list_raises_error(self):
        raw = '{"clause_type": "liability", "verbatim_text": "text"}'
        with pytest.raises(ValueError, match="Expected JSON array"):
            parse_llm_json_list(raw, ExtractedClause)


class TestRiskScoringResult:
    def test_full_risk_result(self):
        raw = '''
        {
            "risk_score": 72,
            "scored_clauses": [
                {"clause_type": "liability", "risk_level": "high", "risk_reason": "Unlimited liability"}
            ],
            "overall_risk_summary": "High risk due to unlimited liability."
        }
        '''
        result = parse_llm_json(raw, RiskScoringResult)
        assert result.risk_score == 72
        assert len(result.scored_clauses) == 1
        assert result.scored_clauses[0].risk_level == "high"
