# Data Collection and API Standards

## Source Selection
- Primary sources preferred over aggregated data
- Minimum 3 independent sources for any factual claim
- Source reliability rating required (A: official docs, B: peer-reviewed, C: community, D: anecdotal)
- All sources must be timestamped — data older than 6 months requires revalidation

## Data Formats
- Raw data stored in JSON Lines format (`.jsonl`)
- Processed data in Parquet format for analytics
- Text data in UTF-8 encoding (no Latin-1 or Windows-1252)
- Date/time fields in ISO 8601 format with timezone (`2024-01-15T10:30:00Z`)

## Collection Rate Limits
- Maximum 10 requests per second to any single API endpoint
- Respect `Retry-After` headers from all APIs
- Implement exponential backoff for rate limit responses (429 status)
- Daily collection budget: 100,000 API calls per source (adjustable per project)

## API Authentication
- API keys stored in environment variables, never in code
- OAuth 2.0 for services that support it (preferred over API key auth)
- Token refresh implemented before expiry (not after 401 response)
- Service accounts used for automated collection (not personal accounts)

## Error Handling for API Calls
When an API call fails, apply this retry policy:

**Maximum retries: 3** with exponential backoff:
- Retry 1: wait 1 second
- Retry 2: wait 4 seconds (1 × 4)
- Retry 3: wait 16 seconds (4 × 4)

After 3 retries, mark the request as **permanently failed** and:
1. Log the failure with full request context (URL, headers minus auth, status code, response body)
2. Add to the failed requests queue for manual review
3. Continue with remaining requests (don't abort the batch)
4. Include failure count in the final report

## Rate Limiting Implementation
```python
class RateLimiter:
    def __init__(self, requests_per_second=10):
        self.rps = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    async def wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
```

## Response Validation
- Validate response schema before processing (schema-first approach)
- Check for empty responses — treat as transient error, retry
- Validate pagination: total count matches sum of pages
- Log response size — flag responses >10MB for review

## Quality Gates — Before Starting Collection
- [ ] Data sources identified and reliability-rated
- [ ] API access confirmed (keys obtained, rate limits documented)
- [ ] Schema defined for collected data
- [ ] Storage location provisioned
- [ ] Ethics review completed (if applicable)
