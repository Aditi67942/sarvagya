# PHASE 2: AI Service Layer Integration
## Building the OCR → NMT → Braille → TTS Engine

---

## 🎯 PHASE 2 OBJECTIVES

Phase 2 transforms the skeleton architecture into a **fully functional AI pipeline** by integrating real AI service SDKs and implementing robust error handling, retry mechanisms, and request/response validation.

---

## 📋 PHASE 2 TASKS BREAKDOWN

### **Task 1: Sarvam AI SDK Integration** [3-4 days]

#### What: Direct SDK instead of raw HTTP
```python
# BEFORE (Phase 1)
async with httpx.AsyncClient() as client:
    response = await client.post(f"{settings.sarvam_base_url}/v1/ocr")

# AFTER (Phase 2)
from sarvam import SarvamClient
client = SarvamClient(api_key=settings.sarvam_api_key)
result = await client.ocr.extract_text(image)
```

#### Why:
- ✅ Official SDK = better error messages
- ✅ Built-in retries + rate limiting
- ✅ Request validation before sending
- ✅ Type hints + IDE autocomplete

#### Implementation Steps:
1. Install Sarvam SDK: `pip install sarvam-ai`
2. Create `services/sarvam_client.py` — thin wrapper around official SDK
3. Replace raw HTTP calls in `ocr_service.py`, `translate_service.py`, `tts_service.py`
4. Add request/response validation
5. Implement exponential backoff retry logic

**Deliverable:**
- [x] `services/sarvam_client.py` — Singleton client instance
- [x] Update all Sarvam service classes to use SDK
- [x] Add retry decorator: `@retry(max_attempts=3, backoff=2)`
- [x] Unit tests for timeout/rate-limit scenarios

---

### **Task 2: Google Vision Service Account Auth** [2-3 days]

#### Current Issue:
- JWT generation happens **inside request** (inefficient)
- No token caching
- Each request regenerates token

#### Phase 2 Solution:
```python
# services/google_vision_client.py
class GoogleVisionClient:
    """Manages OAuth2 token lifecycle."""
    
    def __init__(self, creds_path: str):
        self.creds = self._load_credentials(creds_path)
        self._token = None
        self._token_expiry = None
    
    async def get_access_token(self) -> str:
        """Return cached token or refresh if expired."""
        if self._token and self._token_expiry > time.time() + 300:
            return self._token
        
        # Generate new token
        self._token = self._create_jwt()
        # ... exchange for access token
        return self._token
```

#### Implementation Steps:
1. Create `services/google_vision_client.py` — Token management
2. Move JWT logic to separate `_create_jwt()` method
3. Add token caching with 1-hour expiry
4. Implement refresh-before-expiry pattern
5. Add credential validation on startup

**Deliverable:**
- [x] `services/google_vision_client.py` — Singleton with token caching
- [x] Credential validation in startup hook
- [x] Error detection: missing JSON file, invalid credentials
- [x] Integration tests with mock service account

---

### **Task 3: Gemini Multimodal Vision** [2 days]

#### What: Use Gemini 1.5 Flash for faster OCR
```python
# Cheaper + faster alternative to Pro for simple OCR
"model": "gemini-1.5-flash"  # 80x cheaper than Pro
```

#### Implementation:
1. Monitor Gemini response parsing — different structure than Pro
2. Implement fallback: Flash → Pro if Flash fails
3. Add confidence scoring based on response structure
4. Compare output quality: Pro vs Flash vs Sarvam

**Deliverable:**
- [x] Dual Gemini models (Flash + Pro)
- [x] Quality benchmarking script
- [x] Cost tracking in responses

---

### **Task 4: Liblouis Braille Compilation** [3-4 days]

#### What: Real Liblouis instead of Unicode map

```python
# BEFORE (Phase 1 - fallback only)
GRADE2_CONTRACTIONS = {
    'and': '⠯', 'for': '⠿', ...  # Manual mapping
}

# AFTER (Phase 2 - proper Braille)
import louis
braille = louis.translateString(["en-ueb-g2.ctb"], text)
# Returns: ⠃⠗⠁⠊⠇⠇⠑ ⠛⠗⠁⠙⠉ ⠃ ⠞⠓⠗⠕⠥⠛⠓ ⠏⠮⠏⠑⠗ ⠇⠊⠱⠕⠞⠀⠞⠁⠃⠇⠑⠎
```

#### Why UEB (Unified English Braille) Grade 2:
- ✅ International standard for blind readers
- ✅ Grade 1 (literal) vs Grade 2 (contracted — 50% more compact)
- ✅ UEB = modern, includes literary symbols

#### Implementation:
1. **Install Liblouis:** `pip install louis`
2. **Braille Tables Path:** `louis/tables/` contains `.ctb` files
3. **Grade 2 Tables:** `en-ueb-g2.ctb` (English UEB Grade 2)
4. **Stress Test:** Handle difficult text (numbers, punctuation, emphasis)
5. **Fallback Chain:**
   - Level 1: Liblouis (proper)
   - Level 2: Built-in Grade 2 contractions (Phase 1 fallback)
   - Level 3: Character-by-character conversion (last resort)

#### Code Structure:
```python
class BrailleService:
    def __init__(self):
        self.louis_available = self._check_louis()
    
    def _check_louis(self) -> bool:
        """Detect Liblouis availability at startup."""
        try:
            import louis
            louis.translateString(["en-ueb-g2.ctb"], "test")
            return True
        except:
            return False  # Fallback to Unicode map
    
    def translate(self, text: str) -> BrailleResult:
        """Translate with proper error handling."""
        if self.louis_available:
            try:
                return self._liblouis_translate(text)
            except Exception as e:
                logger.warning(f"Liblouis failed: {e}, falling back...")
        
        return self._fallback_translate(text)
```

**Deliverable:**
- [x] Liblouis integration with fallback
- [x] Multiple table files: UEB Grade 2, Grade 1, Math
- [x] Test suite: numbers, punctuation, emphasis markers
- [x] Startup validation: check Liblouis availability

---

### **Task 5: Consensus Engine v2** [2 days]

#### Enhancement: Confidence-Weighted Voting

**Current Strategy:** Longest text wins
**Better Strategy:** Weighted confidence voting

```python
class ConsensusEngine:
    def resolve(self, results: List[OCRResult]) -> ConsensusResult:
        """Confidence-weighted consensus."""
        
        # Filter successful
        successful = [r for r in results if r.success]
        
        # Calculate weighted score
        weighted_scores = {}
        for result in successful:
            confidence = result.confidence or 0.7
            char_count = len(result.text.strip())
            score = confidence * char_count
            weighted_scores[result.provider] = score
        
        # Pick best
        best_provider = max(weighted_scores, key=weighted_scores.get)
        best = next(r for r in successful if r.provider == best_provider)
        
        return ConsensusResult(
            final_text=best.text.strip(),
            winning_provider=best.provider,
            confidence=weighted_scores[best_provider],
            all_results=results,
        )
```

**Improvements:**
- ✅ Incorporate confidence scores from each provider
- ✅ Penalize short results (may be incomplete)
- ✅ Fuzzy matching to detect duplicates (same text from 2 providers)
- ✅ Logging: show why each provider won/lost

**Deliverable:**
- [x] Weighted consensus algorithm
- [x] Fuzzy matching for duplicate detection
- [x] Detailed debugging output: scores for each provider
- [x] Unit tests with mock OCR results

---

### **Task 6: Error Recovery & Resilience** [3-4 days]

#### Implement Retry Logic

```python
# services/retry.py
from functools import wraps
import asyncio

def retry(max_attempts: int = 3, backoff_factor: float = 2, timeout: int = 10):
    """
    Retry decorator for async functions.
    
    Exponential backoff: 1s → 2s → 4s
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except Exception as e:
                    if attempt == max_attempts:
                        raise  # Final attempt failed
                    
                    wait_time = backoff_factor ** (attempt - 1)
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator

# Usage:
class SarvamOCRService(BaseOCRService):
    @retry(max_attempts=3, backoff_factor=2, timeout=30)
    async def extract_text(self, image_base64: str) -> OCRResult:
        # API call...
```

#### Circuit Breaker Pattern

```python
# services/circuit_breaker.py
class CircuitBreaker:
    """Prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED → OPEN → HALF_OPEN → CLOSED
    
    @asynccontextmanager
    async def execute(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception(f"Circuit breaker OPEN for {self.failure_count} failures")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

#### Graceful Degradation

```python
class Pipeline:
    async def run_pipeline(self, file):
        # Try all OCR methods
        ocr_results = []
        
        try:
            ocr_results.append(await sarvam_ocr.extract_text(image))
        except Exception as e:
            logger.error(f"Sarvam OCR failed: {e}")
        
        try:
            ocr_results.append(await google_ocr.extract_text(image))
        except Exception as e:
            logger.error(f"Google OCR failed: {e}")
        
        # ... more providers
        
        if not ocr_results:
            raise HTTPException(status_code=503, detail="All OCR providers down")
        
        consensus_result = consensus.resolve(ocr_results)
        # Continue with translation + braille + TTS...
```

**Deliverable:**
- [x] `services/retry.py` — Retry decorator
- [x] `services/circuit_breaker.py` — Circuit breaker
- [x] Implement on all external API calls
- [x] Logging: track retry attempts, failures
- [x] Unit tests: simulate timeouts, rate limits

---

### **Task 7: Logging & Monitoring** [2 days]

```python
# core/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging(app: FastAPI):
    """Configure JSON logging for all services."""
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        logger.info({
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration * 1000,
        })
        return response

# Usage:
setup_logging(app)
logger.info({"event": "ocr_start", "provider": "sarvam"})
logger.warning({"event": "ocr_retry", "attempt": 2})
logger.error({"event": "ocr_failed", "error": str(e)})
```

**Deliverable:**
- [x] JSON structured logging
- [x] Request tracing: unique request ID per upload
- [x] Performance metrics: OCR time, translation time, Braille time
- [x] Error tracking: which providers fail most often
- [x] Daily logs file rotation

---

### **Task 8: Testing & Validation** [4-5 days]

#### Unit Tests (Per Service)
```python
# tests/test_ocr_service.py
@pytest.mark.asyncio
async def test_sarvam_ocr_success():
    """Test successful OCR extraction."""
    service = SarvamOCRService()
    result = await service.extract_text(BASE64_SAMPLE_IMAGE)
    assert result.success
    assert len(result.text) > 0
    assert result.confidence > 0.8

@pytest.mark.asyncio
async def test_sarvam_ocr_timeout():
    """Test timeout handling."""
    service = SarvamOCRService()
    # Mock timeout
    with patch("httpx.AsyncClient.post", side_effect=asyncio.TimeoutError):
        result = await service.extract_text(BASE64_SAMPLE_IMAGE)
        assert not result.success
        assert "timeout" in result.error.lower()

# tests/test_consensus_engine.py
def test_consensus_picks_longest():
    """Test consensus picks longest result."""
    results = [
        OCRResult(provider="a", text="short", success=True),
        OCRResult(provider="b", text="this is a much longer text", success=True),
    ]
    consensus = ConsensusEngine()
    result = consensus.resolve(results)
    assert result.winning_provider == "b"

# tests/test_braille_service.py
def test_braille_grade2():
    """Test Braille Grade 2 contraction."""
    service = BrailleService()
    result = service.translate("the cat and the dog")
    # ⠮ = the, ⠯ = and
    assert "⠮" in result.braille_text
    assert "⠯" in result.braille_text
```

#### Integration Tests
```python
# tests/test_pipeline.py
@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete OCR → Translation → Braille → TTS."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/pipeline",
        files={"file": ("test.jpg", SAMPLE_IMAGE, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "ocr" in data
    assert "translation" in data
    assert "braille" in data
    assert "tts" in data
```

#### Load Testing
```python
# tests/load_test.py
import locust

class PipelineLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def upload_file(self):
        with open("test_image.jpg", "rb") as f:
            self.client.post(
                "/api/v1/pipeline",
                files={"file": f}
            )

# Run: locust -f tests/load_test.py -u 10 -r 2 --run-time 5m
```

**Deliverable:**
- [x] Unit tests: >80% code coverage
- [x] Integration tests: full pipeline scenarios
- [x] Mock external APIs (Sarvam, Google, Gemini)
- [x] Load tests: 10+ concurrent uploads
- [x] CI/CD: pytest runs on every commit

---

### **Task 9: Azure Computer Vision (Optional)** [2 days]

If Sarvam/Google/Gemini all fail:
```python
class AzureOCRService(BaseOCRService):
    async def extract_text(self, image_base64: str) -> OCRResult:
        """Azure Computer Vision as 4th backup."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.azure_ocr_endpoint}/vision/v3.2/ocr",
                headers={"Ocp-Apim-Subscription-Key": settings.azure_ocr_key},
                files={"image": base64.b64decode(image_base64)},
            )
            data = response.json()
            text = "\n".join(
                region["text"]
                for line in data["regions"]
                for region in line["lines"]
            )
            return OCRResult(
                provider="azure",
                text=text,
                confidence=0.88,
                success=True,
            )
```

**Deliverable:**
- [x] Azure OCR service class
- [x] Cost comparison: Sarvam vs Google vs Azure
- [x] Dispatch logic: try expensive providers first

---

## 📊 PHASE 2 TIMELINE

| Week | Task(s) | Days |
|------|---------|------|
| 1 | Sarvam SDK integration + Google Vision token caching | 3-4 |
| 2 | Gemini v1.5 integration + Liblouis setup | 3-4 |
| 3 | Error recovery (retry + circuit breaker) + Logging setup | 3-4 |
| 4 | Consensus v2 + Testing suite + Azure (optional) | 4-5 |
| **Total** | **Full AI Service Layer** | **14-17 days** |

---

## 🔄 PHASE 2 → PHASE 3 TRANSITION

**Phase 2 Output:** Working AI pipeline with real Sarvam/Google/Braille/TTS

**Phase 3 Input:** Full API orchestration + React frontend integration

**Phase 3 Focus:**
1. Real frontend testing with live API
2. Accessible UI components (OpenDyslexic, high-contrast)
3. Audio playback + Braille display
4. User session management
5. Analytics/telemetry

---

## 📝 NOTES FOR IMPLEMENTATION

### Error Scenarios to Handle
```python
# Timeout: API takes >30s
# Rate limit: 429 Too Many Requests
# Auth error: 401 Unauthorized (expired token)
# Invalid image: 400 Bad Request (not image)
# Server error: 500 Internal Server Error
# No internet: Connection refused
```

### Confidence Scoring
```python
# Each provider should return confidence 0.0-1.0
# Sarvam: 0.9 (India-optimized)
# Google: 0.95 (high accuracy)
# Gemini: 0.92 (multimodal)
# Azure: 0.88 (less specialized)
```

### Cost Tracking
```python
# Keep per-request cost estimate
# Sarvam OCR: $0.001 per image
# Google Vision: $1.50 per 1000 images
# Gemini Flash: $0.075 per 1M tokens
# Display in API response: "estimated_cost": 0.0015
```

---

**Status:** 📋 Phase 2 Planning Complete  
**Next:** Begin implementation with Sarvam SDK integration  
**Estimated Completion:** 3-4 weeks from start
