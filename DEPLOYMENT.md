# Deployment Guide - ScamShield Honeypot API

## Step 1: Get Free API Keys (15 minutes)

### Groq (NO credit card)
1. Visit: https://console.groq.com/keys
2. Sign up with email
3. Click "Create API Key"
4. Copy: `gsk_xxxxxxxxxxxxx`

### Upstash Redis (NO credit card)
1. Visit: https://console.upstash.com
2. Create account
3. Create new Redis database
4. Copy: `UPSTASH_REDIS_URL`

### Supabase (NO credit card)
1. Visit: https://supabase.com
2. Create new project
3. Go to Settings → API
4. Copy: `SUPABASE_URL` and `SUPABASE_ANON_KEY`
5. Run this SQL in SQL Editor:

```sql
CREATE TABLE honeypot_conversations (
  id SERIAL PRIMARY KEY,
  conversation_id TEXT UNIQUE NOT NULL,
  scam_detected BOOLEAN,
  confidence_score FLOAT,
  scam_type TEXT,
  extracted_intelligence JSONB,
  engagement_metrics JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Step 2: Deploy to Railway (10 minutes)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Navigate to honeypot-api folder
cd honeypot-api

# Initialize
railway init

# Deploy
railway up

# Set environment variables
railway variables set GROQ_API_KEY=your_groq_key
railway variables set UPSTASH_REDIS_URL=your_redis_url
railway variables set SUPABASE_URL=your_supabase_url
railway variables set SUPABASE_KEY=your_supabase_key
railway variables set API_KEY=scamshield_2026_secure_key

# Get your public URL
railway domain
```

## Step 3: Test Your API

```bash
# Health check
curl https://your-app.railway.app/health

# Test honeypot endpoint
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: scamshield_2026_secure_key" \
  -d @test_request.json
```

## Step 4: Submit to Hackathon

**Deployed URL**: `https://your-app.railway.app/api/honeypot`
**API KEY**: `scamshield_2026_secure_key`

## Success Criteria

✅ API responds to health check
✅ Accepts POST requests with x-api-key header
✅ Detects scam intent correctly
✅ Generates believable responses
✅ Extracts UPI IDs, phone numbers, URLs
✅ Returns proper JSON format
✅ Handles multiple conversation turns
✅ Low latency (< 2 seconds per response)
