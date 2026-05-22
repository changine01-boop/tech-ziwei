"""Tests for prompt construction — tone and required fields."""

import pytest

from tech_ziwei.ai.prompts import (
    SYSTEM_PROMPT, STAR_ARCHETYPES, PALACE_DOMAINS,
    core_prompt, relationship_prompt, career_prompt, annual_prompt,
)
from tech_ziwei.engine.constants import MAJOR_STARS, PALACE_NAMES


class TestSystemPrompt:
    def test_covers_all_14_stars(self):
        for star in MAJOR_STARS:
            assert star in SYSTEM_PROMPT, f"Star missing from system prompt: {star}"

    def test_covers_all_12_palaces(self):
        for palace in PALACE_NAMES:
            assert palace in SYSTEM_PROMPT, f"Palace missing from system prompt: {palace}"

    def test_no_fatalistic_language_in_rules(self):
        assert "fatalistic" in SYSTEM_PROMPT.lower() or "deterministic" in SYSTEM_PROMPT.lower()
        # The rule section explicitly forbids these
        assert "Your destiny is" in SYSTEM_PROMPT  # as a forbidden example (✗)

    def test_reflection_question_instruction_present(self):
        assert "Reflection" in SYSTEM_PROMPT

    def test_word_count_reasonable(self):
        word_count = len(SYSTEM_PROMPT.split())
        assert 400 < word_count < 3000


class TestPromptBuilders:
    _dummy_context = "=== BIRTH DATA ===\nGregorian date: 1990-05-15"

    def test_core_prompt_contains_context(self):
        p = core_prompt(self._dummy_context)
        assert self._dummy_context in p
        assert "Life Palace" in p or "命宮" in p

    def test_relationship_prompt_contains_context(self):
        p = relationship_prompt(self._dummy_context)
        assert self._dummy_context in p
        assert "夫妻宮" in p or "Partnership" in p

    def test_career_prompt_contains_context(self):
        p = career_prompt(self._dummy_context)
        assert self._dummy_context in p
        assert "官祿宮" in p or "Career" in p

    def test_annual_prompt_contains_age(self):
        p = annual_prompt(self._dummy_context, current_age=35)
        assert "35" in p
        assert self._dummy_context in p

    def test_all_prompts_non_empty(self):
        for builder, args in [
            (core_prompt, (self._dummy_context,)),
            (relationship_prompt, (self._dummy_context,)),
            (career_prompt, (self._dummy_context,)),
            (annual_prompt, (self._dummy_context, 30)),
        ]:
            result = builder(*args)
            assert len(result) > 100


class TestMappingCompleteness:
    def test_all_14_stars_in_archetypes(self):
        for star in MAJOR_STARS:
            assert star in STAR_ARCHETYPES, f"Missing archetype for {star}"

    def test_all_12_palaces_in_domains(self):
        for palace in PALACE_NAMES:
            assert palace in PALACE_DOMAINS, f"Missing domain for {palace}"

    def test_archetypes_have_psychological_vocabulary(self):
        psychological_terms = {"archetype", "energy", "intelligence", "drive", "pattern", "style", "social", "emotional", "spirit", "mind"}
        for star, desc in STAR_ARCHETYPES.items():
            desc_lower = desc.lower()
            assert any(term in desc_lower for term in psychological_terms), \
                f"Archetype for {star} lacks psychological vocabulary: {desc}"
