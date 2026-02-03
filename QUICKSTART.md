# 🚀 ScamShield AI - Quick Start Guide

## ✅ What's Built

Complete API-based honeypot system for the India AI Impact Buildathon 2026.

**NO voice calling, NO telephony - Just a simple REST API!**

## 📋 Deployment Steps (20 minutes)

### Step 1: Setup Supabase Database (5 min)

1. Go to https://supabase.com/dashboard/project/zzsluvftiuwhmjdabzfg
2. Click **SQL Editor** → **New Query**
3. Copy ALL content from `supabase-setup.sql`
4. Paste and click **Run**
5. Verify: Go to **Table Editor** - you should see `honeypot_conversations` table

### Step 2: Deploy to Railway (10 min)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables (copy from .env file)
railway variables set GROQ_API_KEY=your_groq_key
railway variables set UPSTASH_REDIS_URL=your_redis_url
railway variables set SUPABASE_URL=your_supabase_url
railway variables set SUPABASE_KEY=your_supabase_key
railway variables set API_KEY=scamshield_2026_secure_key

# Deploy
railway up

# Get your public URL
railway domain
```

**Save your Railway URL!** Example: `https://scamshield-production.railway.app`

### Step 3: Test Your API (5 min)

```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test honeypot endpoint
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: scamshield_2026_secure_key" \
  -d @test_request.json
```

## 📊 Expected Response

```json
{
  "status": "success",
  "scam_detected": true,
  "confidence_score": 0.85,
  "scam_type": "lottery_scam",
  "agent_response": "That's great! But I'm confused. Can you share the UPI ID?",
  "conversation_turns": 3,
  "extracted_intelligence": {
    "upi_ids": ["winner@paytm"],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_urls": [],
    "keywords": ["won", "prize", "fee"]
  },
  "engagement_metrics": {
    "conversation_duration_seconds": 30,
    "scammer_engagement_level": "medium",
    "intelligence_quality": "medium"
  }
}
```

## 🎯 For Hackathon Submission

**API Endpoint**: `https://your-app.railway.app/api/honeypot`
**API Key**: `scamshield_2026_secure_key`
**Method**: POST
**Headers**: `x-api-key: scamshield_2026_secure_key`

## ✅ Success Checklist

- [ ] Supabase table created
- [ ] Railway deployed successfully
- [ ] Health endpoint returns 200 OK
- [ ] Honeypot endpoint accepts requests
- [ ] AI generates believable responses
- [ ] Intelligence extracted correctly
- [ ] Data stored in Supabase

## 💰 Total Cost: ₹0

All services use FREE tiers!

## 🐛 Troubleshooting

### Railway deployment fails
```bash
# Check logs
railway logs

# Verify environment variables
railway variables
```

### API returns 401 Unauthorized
- Check that `x-api-key` header is set correctly
- Value should be: `scamshield_2026_secure_key`

### Supabase connection fails
- Verify table was created (run SQL script)
- Check SUPABASE_URL and SUPABASE_KEY in Railway

### Groq API errors
- Verify GROQ_API_KEY is set correctly
- Check you haven't exceeded free tier (14,400 requests/day)

## 📚 Next Steps

1. Test with multiple conversation turns
2. Check Supabase for stored intelligence
3. Monitor Railway logs for any errors
4. Prepare demo for hackathon judges

## 🏆 You're Ready!

Your ScamShield AI Honeypot API is live and ready for the buildathon! 🚀
