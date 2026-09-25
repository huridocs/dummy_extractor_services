#!/usr/bin/env python3
"""Verify the sync POST /translate stub against the Uwazi translationService contract.

Uwazi's ExternalTranslationService (app/api/translationService/infrastructure/ExternalTranslationService.ts)
sends:

    POST {TRANSLATION_SERVICE_URL}/translate?text=..&language_from=..&language_to=..
    body: {}          (empty JSON body; all input is in the query string)
    timeout: 60s

and expects HTTP 200 with {"translated_text": "<string>"}. Anything non-2xx surfaces as
TranslationServiceRequestError, and a 200 without a string translated_text surfaces as
InvalidTranslationResponseError. Both are exercised below.

Requires the dummy service to be running (see `make start-detached`).
Not named test_*.py on purpose: it needs a live server, so unittest/pytest discovery must skip it.
"""

from __future__ import annotations

import sys

import httpx

BASE_URLS = ("http://127.0.0.1:5051", "http://127.0.0.1:5056")

# (text, language_from, language_to, expected_status, expected_body)
# expected_body: dict compared exactly, or None when the response body is not asserted.
CASES: list[tuple[str, str, str, int, dict | None]] = [
    # Known phrases resolve to their stubs.
    ("hola que tal", "es", "en", 200, {"translated_text": "Hello, how are you?"}),
    ("this is a test string", "en", "es", 200, {"translated_text": "Esta es una cadena de prueba"}),
    ("this value will be translated", "en", "fr", 200, {"translated_text": "Cette valeur sera traduite"}),
    ("this value will be translated", "en", "ru", 200, {"translated_text": "Это значение будет переведено"}),
    ("hola que tal", "es", "ar", 200, {"translated_text": "مرحبا، كيف حالك؟"}),
    # Matching is case-insensitive and padding/whitespace is normalized.
    ("  HOLA   Que   Tal ", "es", "en", 200, {"translated_text": "Hello, how are you?"}),
    # Uwazi language codes are ISO-639-1, but 3-letter input is truncated.
    ("hola que tal", "spa", "eng", 200, {"translated_text": "Hello, how are you?"}),
    # Same language echoes the input unchanged.
    ("hola que tal", "es", "es", 200, {"translated_text": "hola que tal"}),
    # Unknown phrases fall back to a deterministic marker.
    ("custom text", "en", "fr", 200, {"translated_text": "[translation for fr] custom text"}),
    # "error" is only special as the whole phrase.
    ("error handling", "en", "fr", 200, {"translated_text": "[translation for fr] error handling"}),
    # Error stubs: non-2xx must reach Uwazi as TranslationServiceRequestError.
    ("error", "en", "fr", 500, {"detail": "translation failed"}),
    ("ERROR", "en", "fr", 500, {"detail": "translation failed"}),
    ("hola", "en", "error", 500, {"detail": "translation failed"}),
    # Missing translated_text on a 200 must reach Uwazi as InvalidTranslationResponseError.
    ("empty", "en", "fr", 200, {}),
    # Validation.
    ("", "en", "fr", 422, None),
]


def check(client: httpx.Client, base: str, case: tuple[str, str, str, int, dict | None]) -> str | None:
    text, language_from, language_to, expected_status, expected_body = case
    label = f"{base} POST /translate?text={text!r}&language_from={language_from}&language_to={language_to}"

    try:
        # json={} reproduces the empty JSON body Uwazi sends.
        response = client.post(
            f"{base}/translate",
            params={"text": text, "language_from": language_from, "language_to": language_to},
            json={},
        )
    except httpx.HTTPError as error:
        return f"{label}\n  request failed: {error!r}"

    if response.status_code != expected_status:
        return f"{label}\n  expected status {expected_status}, got {response.status_code}: {response.text!r}"

    if expected_body is not None:
        try:
            body = response.json()
        except ValueError:
            return f"{label}\n  expected JSON body {expected_body!r}, got non-JSON: {response.text!r}"
        if body != expected_body:
            return f"{label}\n  expected body {expected_body!r}, got {body!r}"

    return None


def check_contract_details(client: httpx.Client, base: str) -> list[str]:
    """The response shape Uwazi's client actually depends on."""
    failures = []

    response = client.post(
        f"{base}/translate",
        params={"text": "hola que tal", "language_from": "es", "language_to": "en"},
        json={},
    )
    translated_text = response.json().get("translated_text")
    if not isinstance(translated_text, str):
        failures.append(f"{base}: translated_text must be a string, got {type(translated_text).__name__}")

    # Uwazi always POSTs; the query-only route must reject the wrong verb.
    wrong_method = client.get(
        f"{base}/translate",
        params={"text": "hi", "language_from": "en", "language_to": "fr"},
    )
    if wrong_method.status_code != 405:
        failures.append(f"{base}: GET /translate should be 405, got {wrong_method.status_code}")

    missing_param = client.post(f"{base}/translate", params={"text": "hi", "language_from": "en"}, json={})
    if missing_param.status_code != 422:
        failures.append(f"{base}: missing language_to should be 422, got {missing_param.status_code}")

    return failures


def main() -> int:
    failures: list[str] = []

    with httpx.Client(timeout=20) as client:
        for base in BASE_URLS:
            try:
                client.get(f"{base}/info").raise_for_status()
            except httpx.HTTPError as error:
                failures.append(f"{base}/info not reachable: {error!r}")
                continue

            for case in CASES:
                failure = check(client, base, case)
                if failure:
                    failures.append(failure)

            failures.extend(check_contract_details(client, base))

    if failures:
        print(f"FAILED: {len(failures)} translate check(s) failed\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    total = len(CASES) * len(BASE_URLS)
    print(f"OK: {total} /translate cases + contract details passed on {', '.join(BASE_URLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
