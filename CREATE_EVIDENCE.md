# 📸 Create Evidence for GUVI

## What to Capture

### 1. GUVI Tester Hanging (Screenshot)
- Open GUVI tester page
- Enter your API URL and key
- Click "Test"
- Wait 2-3 minutes
- Screenshot showing "Processing..." message
- Open browser console (F12)
- Screenshot showing errors:
  - `ERR_NAME_NOT_RESOLVED`
  - `Manifest: Syntax error`

### 2. Vercel Logs (Screenshot)
- Go to https://vercel.com/dashboard
- Select your project
- Click "Logs"
- Show logs during GUVI test time
- Highlight: Only GET requests, NO POST requests
- This proves GUVI never sent the request

### 3. Working Test (Video/Screenshots)

**Terminal Test:**
```bash
# Run this and record/screenshot
python test_guvi_exact_format.py
```

**Show output:**
```
✅ Status Code: 200
✅ All validation checks passed: 6/6
🎉 SUCCESS! YOUR API IS 100% COMPLIANT
```

**cURL Test:**
```bash
curl -X POST https://scamshield-sable.vercel.app/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: scamshield_2026_secure_key" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"test","timestamp":1770005528731},"conversationHistory":[]}'
```

**Show response:**
```json
{"status":"success","reply":"I don't understand. Can you explain?"}
```

### 4. Postman/Insomnia Test (Screenshot)
- Use Postman or Insomnia
- POST to your API endpoint
- Show request and response
- Show response time (<100ms)

## How to Share Evidence

### Create a Document
1. Google Docs or PDF
2. Title: "GUVI API Tester Bug - Evidence"
3. Include all screenshots
4. Add explanations
5. Share link with GUVI support

### Create a Video
1. Use OBS, Loom, or screen recorder
2. Show GUVI tester hanging
3. Show browser console errors
4. Show Vercel logs (no POST requests)
5. Show your tests working
6. Upload to YouTube (unlisted)
7. Share link with GUVI

### Create a GitHub Issue
1. In your repo, create an issue
2. Title: "GUVI Tester Bug - Evidence"
3. Add all screenshots
4. Add test results
5. Share link with GUVI

## Quick Evidence Package

Run these commands and save output:

```bash
# Test 1
python test_guvi_exact_format.py > evidence_test1.txt

# Test 2
python test_request_inspector.py > evidence_test2.txt

# Test 3
curl -X POST https://scamshield-sable.vercel.app/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: scamshield_2026_secure_key" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"test","timestamp":1770005528731},"conversationHistory":[]}' \
  > evidence_curl.txt
```

Zip these files and send to GUVI support.

## What to Say

"My API works perfectly (see evidence), but your tester has a bug and never sends requests. Please manually verify my endpoint or whitelist my submission."
