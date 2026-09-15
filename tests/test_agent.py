"""
Unit tests for src/agent.py.

These tests never call the real OpenAI API: extraction_llm.invoke and
llm.invoke are mocked out with unittest.mock, so the suite runs offline,
free, and fast (no API key required). They deliberately cover the bugs we
hit and fixed manually during development:

- vital signs silently dropped during extraction (US: structured output)
- the SOAP note language not matching the detected source language
- the patient identification header and explicit vital-sign listing
  silently disappearing once the "no preamble" rule started being
  followed literally
- numeric hallucination guardrails staying wired into the prompt

Run with: pytest tests/ -v
"""

from unittest.mock import MagicMock

import pytest

from src.agent import (
    ExtractedEntities,
    VitalSigns,
    check_extraction,
    extract_entities,
    structure_soap,
    verify_soap,
)


# ---------------------------------------------------------------------------
# check_extraction — routing logic (retry loop vs. move on)
# ---------------------------------------------------------------------------

class TestCheckExtraction:
    def test_empty_entities_triggers_retry(self):
        state = {"entities": {}}
        assert check_extraction(state) == "extract_entities"

    def test_missing_symptoms_triggers_retry(self):
        state = {"entities": {"symptoms": []}}
        assert check_extraction(state) == "extract_entities"

    def test_present_symptoms_moves_to_structure_soap(self):
        state = {"entities": {"symptoms": ["chest pain"]}}
        assert check_extraction(state) == "structure_soap"


# ---------------------------------------------------------------------------
# extract_entities — mocked structured-output extraction
# ---------------------------------------------------------------------------

class TestExtractEntities:
    def test_successful_extraction_returns_all_vital_signs(self, monkeypatch):
        """Regression test: vital signs (blood pressure, heart rate,
        temperature, oxygen saturation) must ALL survive extraction, not
        just the first one mentioned in the source text."""
        fake_result = ExtractedEntities(
            patient="John Smith",
            age="52",
            source_language="english",
            symptoms=["shortness of breath", "dizziness"],
            medical_history=["hypertension"],
            vital_signs=VitalSigns(
                blood_pressure="150/95 mmHg",
                heart_rate="110 bpm",
                temperature="",
                oxygen_saturation="94%",
            ),
            medications=["aspirin 300mg"],
            exams=["chest X-ray"],
        )
        mock_extraction_llm = MagicMock()
        mock_extraction_llm.invoke.return_value = fake_result
        monkeypatch.setattr("src.agent.extraction_llm", mock_extraction_llm)

        state = {"raw_text": "John Smith, 52 years old...", "entities": {},
                  "soap_summary": "", "verification_ok": False}
        result = extract_entities(state)

        entities = result["entities"]
        assert entities["vital_signs"]["blood_pressure"] == "150/95 mmHg"
        assert entities["vital_signs"]["heart_rate"] == "110 bpm"
        assert entities["vital_signs"]["oxygen_saturation"] == "94%"
        assert entities["symptoms"] == ["shortness of breath", "dizziness"]

    def test_extraction_failure_returns_empty_entities(self, monkeypatch):
        mock_extraction_llm = MagicMock()
        mock_extraction_llm.invoke.side_effect = ValueError("bad response")
        monkeypatch.setattr("src.agent.extraction_llm", mock_extraction_llm)

        state = {"raw_text": "some text", "entities": {},
                  "soap_summary": "", "verification_ok": False}
        result = extract_entities(state)

        assert result["entities"] == {}


# ---------------------------------------------------------------------------
# structure_soap — mocked generation, asserting on the CONSTRUCTED PROMPT
# ---------------------------------------------------------------------------

class TestStructureSoap:
    """These tests assert on the messages sent to the LLM, not on what the
    LLM would actually do with them — we can't test LLM compliance
    offline. What we CAN guarantee deterministically is that structure_soap
    builds the correct instructions and includes all available data, which
    is the part of the recurring language / vitals / patient-header bugs
    that was under our control.

    structure_soap now calls llm.invoke([SystemMessage, HumanMessage]) —
    the language directive lives in the SystemMessage, everything else in
    the HumanMessage. Tests inspect both.
    """

    def _mock_llm(self, monkeypatch, response_text="Patient: ...\nAge: ...\n\nS - Subjective: ...\nO - Objective: ...\nA - Assessment: ...\nP - Plan: ..."):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content=response_text)
        monkeypatch.setattr("src.agent.llm", mock_llm)
        return mock_llm

    @staticmethod
    def _sent_messages(mock_llm):
        messages = mock_llm.invoke.call_args[0][0]
        system_content = messages[0].content
        human_content = messages[1].content
        return system_content, human_content

    def test_prompt_targets_french_for_french_source(self, monkeypatch):
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "Jean Dupont, 45 ans. Douleur thoracique ce matin.",
            "entities": {"source_language": "french", "symptoms": ["douleur thoracique"], "vital_signs": {}},
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        system_content, human_content = self._sent_messages(mock_llm)
        assert "MUST be in French" in system_content
        assert "MUST be in English" not in system_content
        assert "required output language is French" in human_content

    def test_prompt_targets_english_for_english_source(self, monkeypatch):
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "John Smith, 52 years old. Shortness of breath.",
            "entities": {"source_language": "english", "symptoms": ["shortness of breath"], "vital_signs": {}},
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        system_content, human_content = self._sent_messages(mock_llm)
        assert "MUST be in English" in system_content
        assert "MUST be in French" not in system_content
        assert "required output language is English" in human_content

    def test_unrecognized_source_language_falls_back_to_english(self, monkeypatch):
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "Juan Perez, 52 años.",
            "entities": {"source_language": "other", "symptoms": ["dolor"], "vital_signs": {}},
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        system_content, _ = self._sent_messages(mock_llm)
        assert "MUST be in English" in system_content

    def test_prompt_includes_all_provided_vital_signs(self, monkeypatch):
        """Regression test for the omission bug: every non-empty vital
        sign must appear in the JSON blob injected into the human message,
        AND the instruction to list each one explicitly must be present."""
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "John Smith, 52 years old.",
            "entities": {
                "source_language": "english",
                "symptoms": ["dizziness"],
                "vital_signs": {
                    "blood_pressure": "150/95 mmHg",
                    "heart_rate": "110 bpm",
                    "temperature": "",
                    "oxygen_saturation": "94%",
                },
            },
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        _, human_content = self._sent_messages(mock_llm)
        assert "150/95 mmHg" in human_content
        assert "110 bpm" in human_content
        assert "94%" in human_content
        assert "EXPLICITLY list each vital sign" in human_content

    def test_prompt_requires_patient_header(self, monkeypatch):
        """Regression test: the patient identification header (name, age)
        must be explicitly required, not left to the model's discretion —
        this is what silently disappeared when the 'no preamble' rule
        started being followed literally."""
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "John Smith, 52 years old.",
            "entities": {"source_language": "english", "symptoms": ["dizziness"], "vital_signs": {}},
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        _, human_content = self._sent_messages(mock_llm)
        assert "patient identification header" in human_content
        assert "REQUIRED" in human_content

    def test_prompt_forbids_inventing_numeric_values(self, monkeypatch):
        """Regression test for the hallucinated-blood-pressure bug: the
        anti-hallucination guardrail must stay present in the prompt."""
        mock_llm = self._mock_llm(monkeypatch)
        state = {
            "raw_text": "John Smith, 52 years old.",
            "entities": {"source_language": "english", "symptoms": ["dizziness"], "vital_signs": {}},
            "soap_summary": "",
            "verification_ok": False,
        }

        structure_soap(state)

        _, human_content = self._sent_messages(mock_llm)
        assert "Do not invent or alter ANY numeric value" in human_content


# ---------------------------------------------------------------------------
# verify_soap
# ---------------------------------------------------------------------------

class TestVerifySoap:
    def test_ok_response_marks_verified(self, monkeypatch):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="OK")
        monkeypatch.setattr("src.agent.llm", mock_llm)

        state = {"raw_text": "", "entities": {}, "soap_summary": "S...O...A...P...",
                  "verification_ok": False}
        result = verify_soap(state)

        assert result["verification_ok"] is True
        assert "soap_summary" not in result  # unchanged, left untouched

    def test_not_ok_response_appends_warning(self, monkeypatch):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="NOT OK")
        monkeypatch.setattr("src.agent.llm", mock_llm)

        state = {"raw_text": "", "entities": {}, "soap_summary": "S...O...",
                  "verification_ok": False}
        result = verify_soap(state)

        assert result["verification_ok"] is False
        assert "incomplete" in result["soap_summary"].lower() or "incomplet" in result["soap_summary"].lower()
        assert result["soap_summary"].startswith("S...O...")