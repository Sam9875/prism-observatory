"""Input and output rails, executed through Guardrails AI Guards."""

from __future__ import annotations

import re
from dataclasses import dataclass

from guardrails.settings import settings

settings.rc.enable_metrics = False

from guardrails import Guard, OnFailAction
from guardrails.validator_base import FailResult, PassResult, Validator, register_validator

INJECTION_PATTERNS = (
    r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|prompts|rules)",
    r"disregard\s+(?:the\s+)?(?:system|previous|prior)",
    r"you\s+are\s+now",
    r"\bjailbreak\b",
    r"system\s+prompt",
    r"reveal\s+(?:your|the)\s+(?:system\s+)?(?:prompt|instructions)",
    r"do\s+anything\s+now",
    r"\bDAN\b",
    r"developer\s+mode",
    r"bypass\s+(?:the\s+)?(?:guard|rail|filter|safety)",
)

EMAIL = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b")
PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s])?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
CITE_SPLIT = re.compile(r"(.*?)\[(\d+)\]", re.S)
MAX_CHARS = 400

BLOCKED = {
    "empty": "PRISM stopped this at the input rail. The question was empty.",
    "length": "PRISM stopped this at the input rail. Ask one question in 400 characters or fewer.",
    "injection": "PRISM stopped this at the input rail. The question tries to override the observatory instructions, so nothing was retrieved.",
    "pii": "PRISM stopped this at the input rail. The question contains personal data such as an email, phone number, or account number. Remove it and ask again.",
    "grounding": "PRISM stopped this at the output rail. The draft answer was not supported by the cited passages.",
}


@dataclass
class RailReport:
    passed: bool
    rail: str
    message: str
    text: str
    detail: str
    citations: list[dict] | None = None

    @property
    def repaired(self) -> bool:
        return self.rail == "repaired"


def _norm(text: str) -> str:
    return " ".join(text.split())


def analyze_input(question: str) -> RailReport:
    text = (question or "").strip()
    if not text:
        return RailReport(False, "empty", BLOCKED["empty"], text, "Input rail blocked an empty question.")
    if len(text) > MAX_CHARS:
        return RailReport(False, "length", BLOCKED["length"], text, "Input rail blocked a question over 400 characters.")
    folded = text.casefold()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, folded if "DAN" not in pattern else text, re.I):
            return RailReport(False, "injection", BLOCKED["injection"], text, "Input rail blocked an instruction-override attempt.")
    if EMAIL.search(text) or SSN.search(text) or CARD.search(text) or PHONE.search(text):
        return RailReport(False, "pii", BLOCKED["pii"], text, "Input rail blocked personal data in the question.")
    return RailReport(True, "clear", "", text, "Input rail passed. No override attempt or personal data.")


def analyze_output(answer: str, citations: list[dict], chunks: list[dict]) -> RailReport:
    text = answer or ""
    if not text.strip() or text.startswith("PRISM stopped this") or "does not have grounded material" in text:
        return RailReport(True, "clear", "", text, "Output rail passed. The refusal is an allowed result.", citations)
    by_id = {}
    for chunk in chunks:
        chunk_id = chunk.get("chunk_id") or chunk.get("id")
        if chunk_id:
            by_id[chunk_id] = chunk.get("text") or ""
    comparative = text.startswith("Set side by side")
    body = re.sub(r"^Set side by side, the archives say this\.\s*", "", text)
    body = re.sub(r"\s*Grounded in \d+ passage\(s\)\.\s*$", "", body)
    kept_sentences: list[str] = []
    kept_citations: list[dict] = []
    seen: set[str] = set()
    dropped = 0
    matches = list(CITE_SPLIT.finditer(body))
    if not matches:
        dropped = 1
    for match in matches:
        number = int(match.group(2))
        bare = _norm(match.group(1))
        citation = next((item for item in citations if item.get("n") == number), None)
        passage = by_id.get(citation.get("chunk_id"), "") if citation else ""
        if citation and bare and bare in _norm(passage):
            chunk_id = citation.get("chunk_id")
            if chunk_id not in seen:
                seen.add(chunk_id)
                kept = dict(citation)
                kept["n"] = len(kept_citations) + 1
                kept_citations.append(kept)
            marker = next(item["n"] for item in kept_citations if item.get("chunk_id") == chunk_id)
            kept_sentences.append(f"{bare} [{marker}]")
        else:
            dropped += 1
    if not kept_sentences:
        return RailReport(False, "grounding", BLOCKED["grounding"], BLOCKED["grounding"], "Output rail rejected an answer that was not in the cited passages.", [])
    prefix = "Set side by side, the archives say this. " if comparative else ""
    repaired = prefix + " ".join(kept_sentences) + f"\n\nGrounded in {len(kept_citations)} passage(s)."
    if dropped:
        return RailReport(True, "repaired", "", repaired, f"Output rail removed {dropped} sentence(s) that were not in the cited passages.", kept_citations)
    return RailReport(True, "clear", "", text, "Output rail passed. Every cited sentence is in its passage.", citations)


@register_validator(name="prism/input-safety", data_type="string")
class InputSafety(Validator):
    def _validate(self, value, metadata):  # noqa: ANN001
        report = analyze_input(str(value or ""))
        if report.passed:
            return PassResult()
        return FailResult(error_message=report.message)


@register_validator(name="prism/grounded-output", data_type="string")
class GroundedOutput(Validator):
    def _validate(self, value, metadata):  # noqa: ANN001
        meta = metadata or {}
        report = analyze_output(str(value or ""), list(meta.get("citations") or []), list(meta.get("chunks") or []))
        if report.passed and report.rail != "repaired":
            return PassResult()
        return FailResult(error_message=report.message or report.detail, fix_value=report.text)


def _silence(guard: Guard) -> Guard:
    telemetry = getattr(guard, "_hub_telemetry", None)
    if telemetry is None:
        return guard
    telemetry._enabled = False
    processor = getattr(telemetry, "_processor", None)
    if processor is not None and not getattr(telemetry, "_prism_silenced", False):
        processor.shutdown()
        telemetry._prism_silenced = True
    return guard


_original_load_rc = Guard._load_rc


def _load_rc_quiet(self) -> None:
    _original_load_rc(self)
    settings.rc.enable_metrics = False


Guard._load_rc = _load_rc_quiet


def _guard(validator: Validator) -> Guard:
    settings.rc.enable_metrics = False
    return _silence(Guard().use(validator))


def screen_input(question: str) -> RailReport:
    report = analyze_input(question)
    outcome = _guard(InputSafety(on_fail=OnFailAction.NOOP)).validate(question)
    if bool(outcome.validation_passed) != report.passed:
        raise RuntimeError("Guardrails input rail disagreed with the local check")
    return report


def screen_output(answer: str, citations: list[dict], chunks: list[dict]) -> RailReport:
    report = analyze_output(answer, citations, chunks)
    outcome = _guard(GroundedOutput(on_fail=OnFailAction.NOOP)).validate(
        answer,
        metadata={"citations": citations, "chunks": chunks},
    )
    guard_passed = bool(outcome.validation_passed)
    if guard_passed != (report.passed and report.rail != "repaired"):
        raise RuntimeError("Guardrails output rail disagreed with the local check")
    return report
