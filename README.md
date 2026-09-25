### To run the dummy service: 

```bash
make docker 
```

### Alternatively, to run the dummy service:

```bash
make install_venv
make start
```


### Dummy service for 

1. pdf_paragraphs_extraction
2. pdf_metadata_extraction
3. docker-translation-service (Redis queues via `worker_translations.py`)
4. sync HTTP translate for Uwazi `translationService` (`POST /translate`)

### Sync translate (`POST /translate`)

Used by Uwazi `POST /api/translationService`. Same FastAPI app on ports **5051** and **5056**.

```bash
curl -sS -X POST "http://127.0.0.1:5051/translate?text=hola%20que%20tal&language_from=es&language_to=en"
# {"translated_text":"Hello, how are you?"}
```

Stubbed source phrases (case-insensitive) for `en` / `fr` / `es` / `ru` / `ar`:

- `hola que tal`
- `this is a test string`
- `this value will be translated`

Other text returns `"[translation for {language_to}] {text}"`.

Error stubs (no delays):

- `text=error` or `language_to=error` → HTTP 500 `{ "detail": "translation failed" }`
- `text=empty` → HTTP 200 `{}` (missing `translated_text`)

Point Uwazi at the dummy:

```bash
FEATURE_FLAG_TRANSLATION_SERVICE=true
TRANSLATION_SERVICE_URL=http://localhost:5051
```
