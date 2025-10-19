# 🚀 AI Content System - Quick Start Guide

## ⚡ 5-Minute Setup

### **Step 1: Start the Backend**
```bash
cd ai_content_system
source venv/bin/activate
python src/main.py
```
✅ Backend running at: http://localhost:5000

### **Step 2: Start the Dashboard**
```bash
cd ai-content-dashboard  
pnpm run dev --host
```
✅ Dashboard running at: http://localhost:5173

### **Step 3: Add Your First Keywords**
1. Open dashboard: http://localhost:5173
2. Go to **Keywords** → Click **Add Keyword**
3. Add keywords like: "artificial intelligence", "climate change", "cryptocurrency"
4. Select appropriate categories and priorities

### **Step 4: Monitor Trends**
1. Go to **Trends** section
2. Click **Start Monitoring** 
3. Watch as trending topics appear in real-time
4. Click **Generate Article** on any interesting trend

### **Step 5: Manage Generated Content**
1. Go to **Articles** section
2. Review generated articles
3. Update status: Draft → Review → Approved → Published
4. Edit content as needed before publishing

## 🎯 Common Use Cases

### **Daily News Operation**
```bash
# Morning routine
1. Check trending topics from overnight
2. Generate 5-10 articles from top trends  
3. Review and approve quality content
4. Publish to main news website
```

### **Breaking News Response**
```bash
# When major news breaks
1. Add breaking news keywords immediately
2. Start monitoring for related trends
3. Generate multiple angle articles quickly
4. Beat competitors to market with AI speed
```

### **Content Planning**
```bash
# Weekly content strategy
1. Analyze trending topics by category
2. Identify content gaps and opportunities  
3. Generate evergreen content from stable trends
4. Plan editorial calendar around AI insights
```

## 🔧 Essential API Endpoints

### **Quick Article Generation**
```bash
curl -X POST http://localhost:5000/api/ai/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Latest AI developments",
    "category": "Technology", 
    "provider": "openai",
    "target_length": 800
  }'
```

### **Add Monitoring Keywords**
```bash
curl -X POST http://localhost:5000/api/ai/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "climate summit",
    "category": "World Affairs",
    "priority": 4
  }'
```

### **Start Trend Monitoring**
```bash
curl -X POST http://localhost:5000/api/ai/trends/monitor \
  -H "Content-Type: application/json" \
  -d '{"hours_back": 24}'
```

## 💡 Pro Tips

### **Keyword Strategy**
- ✅ Use specific, newsworthy terms
- ✅ Mix broad topics with niche subjects  
- ✅ Update keywords based on current events
- ✅ Set higher priority for breaking news terms

### **Content Quality**
- ✅ Always review AI-generated content
- ✅ Add human insights and local context
- ✅ Verify facts and sources before publishing
- ✅ Maintain your publication's voice and style

### **Cost Optimization**
- ✅ Use Deepseek for high-volume, basic content
- ✅ Use OpenAI for premium, complex articles
- ✅ Monitor token usage in dashboard
- ✅ Set daily/monthly generation limits

## 🚨 Troubleshooting

### **Backend Won't Start**
```bash
# Check if port 5000 is available
lsof -i :5000

# Restart with different port
export FLASK_RUN_PORT=5001
python src/main.py
```

### **Dashboard Connection Issues**
```bash
# Check API connectivity
curl http://localhost:5000/api/ai/keywords

# Restart React dev server
pnpm run dev --host --port 3000
```

### **No Trends Appearing**
1. Verify keywords are added and active
2. Check internet connectivity for external APIs
3. Review monitoring logs in backend console
4. Try manual trend monitoring with broader keywords

## 📊 Success Metrics to Track

### **Daily Targets**
- 🎯 **10-20 trending topics** detected
- 🎯 **5-10 articles** generated  
- 🎯 **80%+ approval rate** for generated content
- 🎯 **<$2.00 daily cost** for content generation

### **Weekly Goals**
- 🎯 **50+ published articles** from AI generation
- 🎯 **90%+ uptime** for monitoring system
- 🎯 **3-5 new keywords** added based on trends
- 🎯 **Competitive content coverage** of major stories

---

## 🎉 You're Ready to Go!

Your AI Content Generation System is now operational and ready to transform your news operation. The system will continuously monitor trends, generate high-quality articles, and help you stay ahead of the competition with automated, intelligent content creation.

**Need Help?** Check the full documentation in `AI_CONTENT_SYSTEM_DOCUMENTATION.md` for detailed configuration options and advanced features.

