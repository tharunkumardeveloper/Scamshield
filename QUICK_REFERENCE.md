# ⚡ Quick Reference - GUVI Competition

## 🎯 Your API Endpoint

```
POST https://your-project.vercel.app/api/honeypot
```

## 🔑 Authentication

```
Header: x-api-key: your-secret-key
```

## 📥 Request Format

```json
{
  "sessionId": "session-id",
  "message": {
    "sender": "scammer",
    "text": "Message text",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

## 📤 Response Format

```json
{
  "status": "success",
  "reply": "Agent's response"
}
```

## 🚀 Deploy Commands

```bash
# Deploy to Vercel
vercel --prod

# View logs
vercel logs

# Test locally
python main.py
python test_api.py
```

## 🔧 Environment Variables

```env
GROQ_API_KEY=gsk_your_groq_key
API_KEY=your-secret-api-key
```

## ✅ Pre-Submission Checklist

- [ ] Groq API key obtained
- [ ] Deployed to Vercel/Railway
- [ ] Environment variables set
- [ ] Tested with test_api.py
- [ ] API endpoint is public
- [ ] Returns correct format
- [ ] Multi-turn conversations work
- [ ] Intelligence extraction working
- [ ] Final callback implemented

## 🧪 Quick Test

```bash
curl -X POST https://your-api.vercel.app/api/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-key" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Verify now!",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

## 📊 What Gets Evaluated

1. **Scam Detection** - Identifies scam messages
2. **Engagement** - Number of conversation turns
3. **Intelligence** - UPI IDs, accounts, URLs extracted
4. **Stability** - API uptime and response time
5. **Ethics** - No harassment or illegal actions

## 🎓 Submission Steps

1. Deploy to Vercel
2. Get your API URL
3. Go to GUVI platform
4. Submit API endpoint + API key
5. Test endpoint on platform
6. Submit for evaluation

## 📞 Important URLs

- **Groq Console**: https://console.groq.com
- **Vercel Dashboard**: https://vercel.com
- **GitHub Repo**: https://github.com/tharunkumardeveloper/Scamshield
- **GUVI Callback**: https://hackathon.guvi.in/api/updateHoneyPotFinalResult

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| 401 Error | Check x-api-key header |
| 500 Error | Verify GROQ_API_KEY is set |
| Timeout | Check Groq API limits |
| No callback | Need 5+ turns with intelligence |

## 📚 Documentation Files

- `COMPETITION_README.md` - Full competition guide
- `DEPLOYMENT_GUIDE.md` - Step-by-step deployment
- `SUMMARY.md` - Implementation details
- `README.md` - General project info

## 💡 Pro Tips

1. Test locally before deploying
2. Monitor Vercel logs during evaluation
3. Groq free tier: 30 req/min
4. Keep responses short (1-2 sentences)
5. Let agent run 5+ turns for best score

---

**Ready to submit?** Follow DEPLOYMENT_GUIDE.md

**Need help?** Check SUMMARY.md for details

**Good luck!** 🍀
