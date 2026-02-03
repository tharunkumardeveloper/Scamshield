# 🚀 Deployment Guide for GUVI Competition

## Prerequisites

- GitHub account
- Vercel account (or Railway account)
- Groq API key (get from https://console.groq.com)

## Step 1: Get Groq API Key

1. Go to https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it for deployment)

## Step 2: Deploy to Vercel (Recommended)

### Option A: Deploy via Vercel Dashboard

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `API_KEY`: Create a secure random string (this is your API authentication key)
5. Click "Deploy"
6. Wait for deployment to complete
7. Copy your deployment URL (e.g., `https://your-project.vercel.app`)

### Option B: Deploy via CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add GROQ_API_KEY
vercel env add API_KEY

# Redeploy with env vars
vercel --prod
```

## Step 3: Test Your Deployment

### Update test_api.py

```python
# In test_api.py, update:
API_URL = "https://your-project.vercel.app/api/honeypot"
API_KEY = "your-api-key-from-vercel"
```

### Run Tests

```bash
python test_api.py
```

You should see:
- ✅ Status Code: 200
- ✅ Response with "status": "success"
- ✅ Agent reply in response

## Step 4: Submit to GUVI Platform

1. Go to GUVI competition platform
2. Navigate to "API Endpoint Submission"
3. Enter your details:
   - **API Endpoint URL**: `https://your-project.vercel.app/api/honeypot`
   - **API Key**: Your API_KEY from environment variables
4. Click "Test Endpoint" to verify
5. Submit for evaluation

## Step 5: Monitor Your Submission

### Check Vercel Logs

```bash
vercel logs
```

Or view logs in Vercel dashboard:
1. Go to your project
2. Click "Deployments"
3. Click on latest deployment
4. View "Functions" logs

### What to Look For

- ✅ Incoming requests from GUVI platform
- ✅ Scam detection working
- ✅ Agent responses generated
- ✅ Final callbacks sent to GUVI endpoint
- ❌ Any errors or timeouts

## Alternative: Deploy to Railway

### Railway Deployment

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables:
   - `GROQ_API_KEY`
   - `API_KEY`
5. Railway will auto-detect Python and deploy
6. Copy your Railway URL

## Troubleshooting

### Issue: 401 Unauthorized

**Solution**: Check that x-api-key header matches your API_KEY environment variable

### Issue: 500 Internal Server Error

**Solution**: 
- Check Groq API key is valid
- Check logs for specific error
- Verify all dependencies in requirements.txt

### Issue: Timeout

**Solution**:
- Groq API might be slow, increase timeout
- Check your Groq API rate limits
- Consider adding fallback responses

### Issue: Final Callback Not Sent

**Solution**:
- Check conversation has 5+ turns with intelligence
- Verify scam was detected
- Check logs for callback errors

## Testing Checklist

Before submitting:

- [ ] API endpoint is publicly accessible
- [ ] GET / returns service information
- [ ] GET /health returns healthy status
- [ ] POST /api/honeypot accepts correct format
- [ ] API key authentication works
- [ ] Scam detection identifies scams
- [ ] Agent generates human-like responses
- [ ] Intelligence extraction works
- [ ] Multi-turn conversations maintain context
- [ ] Final callback sends to GUVI endpoint

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | `gsk_...` |
| `API_KEY` | Your API authentication key | `my-secret-key-123` |

## Support

If you encounter issues:
1. Check Vercel/Railway logs
2. Run local tests with `python test_api.py`
3. Verify environment variables are set
4. Check COMPETITION_README.md for details

## Quick Commands

```bash
# Test locally
python main.py
python test_api.py

# Deploy to Vercel
vercel --prod

# View logs
vercel logs

# Check deployment status
vercel ls
```

Good luck with the competition! 🍀
