# InfluencerFlow AI/ML Backend Services

A comprehensive AI-powered influencer marketing platform built with Google Gemini, featuring semantic creator discovery, automated outreach, intelligent negotiation, and contract automation.

## 🚀 Architecture Overview

The InfluencerFlow platform consists of 5 microservices, each specialized for different aspects of influencer marketing automation:

### Core Services

1. **Creator Discovery Service** (Port 8001)
   - AI-powered semantic search using Gemini embeddings
   - Advanced creator recommendation algorithms
   - Comprehensive filtering and categorization
   - Vector similarity search with Redis caching

2. **AI Communication Service** (Port 8002)  
   - Personalized outreach message generation
   - Automated negotiation handling
   - Voice message generation (ElevenLabs integration)
   - Content analysis and brand safety checks

3. **Contract Automation Service** (Port 8003)
   - AI-generated legal documents
   - Compliance checking and validation
   - Multiple contract templates
   - Digital signature integration

4. **Analytics Engine Service** (Port 8004)
   - Performance prediction algorithms
   - Campaign optimization recommendations
   - Social media metrics aggregation
   - ROI calculation and reporting

5. **API Gateway Service** (Port 8000)
   - Unified API interface for web frontend
   - Service orchestration and routing
   - Authentication and rate limiting
   - End-to-end workflow automation

## 🛠️ Technology Stack

- **AI Framework**: Google Gemini API for language understanding and generation
- **Backend**: FastAPI with async/await support
- **Database**: PostgreSQL for relational data, Redis for caching
- **Vector Storage**: Redis with custom vector operations
- **Language**: Python 3.11 with modern async patterns

## 📋 Prerequisites

- Google Gemini API key (required)
- ElevenLabs API key (optional, for voice features)
- DeepL API key (optional, for translations)

## 🚀 Quick Start (Local Development)

### 1. Clone and Setup

```bash
# Navigate to your project directory
cd backend/ai_services

# Copy environment variables
cp .env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

### 2. Configure Environment Variables

Edit the `.env` file and add your API keys:

```bash
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional: Additional services
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
DEEPL_API_KEY=your_deepl_api_key_here
```

### 3. Start Services (Local)

```bash
# Start PostgreSQL and Redis (ensure they are running)
# Start each microservice in a separate terminal:
cd backend/ai_services/creator_discovery && python main.py
cd backend/ai_services/ai_communication && python main.py
cd backend/ai_services/contract_automation && python main.py
cd backend/ai_services/analytics_engine && python main.py
cd backend/ai_services/api_gateway && python main.py
```

### 4. Verify Installation

- API Gateway: http://localhost:8000/health
- Creator Discovery: http://localhost:8001/health
- AI Communication: http://localhost:8002/health
- Contract Automation: http://localhost:8003/health
- Analytics Engine: http://localhost:8004/health

## 📊 API Documentation

Once services are running, access interactive API documentation:

- **API Gateway**: http://localhost:8000/docs
- **Creator Discovery**: http://localhost:8001/docs  
- **AI Communication**: http://localhost:8002/docs
- **Contract Automation**: http://localhost:8003/docs
- **Analytics Engine**: http://localhost:8004/docs


## 🚦 API Endpoints for Frontend Integration

All endpoints are available via the **API Gateway** (default: `http://localhost:8000/`).

---

### **Campaign Management**

#### **Create a Campaign**
- **POST** `/api/v1/campaigns`
- **Description:** Create a new campaign.
- **Body Example:**
    ```json
    {
      "brand_name": "EcoStyle Apparel",
      "campaign_name": "Sustainable Summer Collection",
      "target_audience": "Eco-conscious millennials and Gen Z, ages 18-35",
      "budget_range": "$3000-7000",
      "timeline": "30 days",
      "platforms": ["Instagram", "TikTok", "Pinterest"],
      "content_types": ["unboxing", "outfit_ideas", "sustainability_tips"],
      "campaign_goals": ["brand_awareness", "social_engagement", "website_traffic"],
      "deliverables": [
        {
          "type": "Instagram Reel",
          "description": "Create and post a 30-second Instagram Reel showcasing the new collection.",
          "quantity": 2,
          "due_date": "2024-08-10"
        }
      ],
      "start_date": "2024-08-01",
      "end_date": "2024-08-31"
    }
    ```

#### **List All Campaigns**
- **GET** `/api/v1/campaigns`
- **Description:** List all campaigns.

#### **Get Campaign Details**
- **GET** `/api/v1/campaigns/{campaign_id}`
- **Description:** Get details for a specific campaign.

---

### **AI-Powered Features**

All endpoints below are available via `http://localhost:8000/api/v1/ai/`.

---

#### **Creator Discovery**

- **POST** `/creators/search`
- **Description:** Search and filter creators across platforms.
- **Body Example:**
    ```json
    {
      "query": "fitness influencers in the US",
      "platform": "Instagram",
      "category": "fitness",
      "min_followers": 5000
    }
    ```

---

#### **Outreach Message Generation**

- **POST** `/communication/generate-outreach`
- **Description:** Generate a personalized outreach message for a creator.
- **Body Example:**
    ```json
    {
    "creator_profile": {
        "name": "Alex Chen",
        "platform": "YouTube",
        "content_style": "tech reviews"
    },
    "campaign_brief": {
        "brand_name": "TechGadgets Inc",
        "campaign_name": "Smart Home Launch",
        "goal": "brand_awareness"
      },
      "message_type": "initial_outreach"
    }
    ```

---

#### **Negotiation**

- **POST** `/negotiation/start`
- **Description:** Start a negotiation with a creator.
- **Body Example:**
    ```json
    {
      "creator_profile": {
        "name": "Alex Chen",
        "platform": "YouTube",
        "followers": 300000
      },
      "campaign_brief": {
        "brand_name": "TechGadgets Inc",
        "campaign_name": "Smart Home Launch",
        "goal": "brand_awareness"
      },
      "brand_constraints": {
        "max_budget": 1500
      }
    }
    ```

- **POST** `/negotiation/respond`
- **Description:** Respond to an ongoing negotiation.
- **Body Example:**
    ```json
    {
      "negotiation_id": "neg_123",
      "creator_response": {
        "message": "Can we increase the budget?"
      },
      "creator_profile": {
        "name": "Alex Chen",
        "platform": "YouTube",
        "followers": 300000
      },
      "campaign_brief": {
        "brand_name": "TechGadgets Inc",
        "campaign_name": "Smart Home Launch",
        "goal": "brand_awareness"
      },
      "brand_constraints": {
        "max_budget": 1500
      }
    }
    ```

---

#### **Contract Generation**

- **POST** `/generate-contract`
- **Description:** Generate a contract for a campaign and creator.
- **Body Example:**
    ```json
    {
      "deal_terms": {
        "brand_name": "EcoStyle Apparel",
        "influencer_name": "Jamie Lee",
        "platform": "Instagram",
        "campaign_name": "Sustainable Summer Collection",
        "total_fee": 3500,
        "deliverables": [
          {
            "type": "Instagram Reel",
            "description": "Create and post a 30-second Instagram Reel showcasing the new collection.",
            "quantity": 2,
            "due_date": "2024-08-10"
          }
        ],
        "start_date": "2024-08-01",
        "end_date": "2024-08-31"
      }
    }
    ```

---

#### **Analytics**

- **POST** `/analytics/analyze-campaign`
- **Description:** Analyze campaign performance.
- **Body Example:**
    ```json
    {
      "campaign_id": "camp_123",
      "metrics": {
        "reach": true,
        "engagement": true
      },
      "time_period": {
        "start_date": "2024-05-01",
        "end_date": "2024-05-31"
      }
    }
    ```

- **POST** `/analytics/predict-performance`
- **Description:** Predict campaign performance.
- **Body Example:**
    ```json
    {
      "creator_profile": {
        "creator_id": "creator_1",
        "name": "Sarah Johnson",
        "platform": "Instagram",
        "followers": 150000,
        "engagement_rate": 4.2
      },
      "campaign_details": {
        "campaign_id": "camp_123",
        "brand_name": "EcoStyle Apparel",
        "campaign_name": "Sustainable Summer Collection",
        "target_audience": "Eco-conscious millennials and Gen Z, ages 18-35",
        "budget_range": "$3000-7000",
        "timeline": "30 days",
        "platforms": ["Instagram", "TikTok", "Pinterest"],
        "content_types": ["unboxing", "outfit_ideas", "sustainability_tips"],
        "campaign_goals": ["brand_awareness", "social_engagement", "website_traffic"]
      },
      "historical_data": [
        {
          "metric": "impressions",
          "predicted_value": 50000,
          "confidence_score": 0.85,
          "factors_considered": ["historical engagement", "audience match"]
        }
      ]
    }
    ```

---

## 🧑‍💻 **How to Use**

- **Campaign management endpoints** are at `/api/v1/campaigns`.
- **AI-powered endpoints** are at `/api/v1/ai/...`.
- For more details and schemas, see the [Swagger docs](http://localhost:8000/docs).

## 📁 Project Structure

```
backend/ai_services/
├── shared/                    # Shared utilities and configuration
│   ├── config.py             # Global settings and demo data
│   ├── database.py           # PostgreSQL models and connections
│   ├── redis_client.py       # Redis caching operations
│   ├── vector_store.py       # Vector similarity search
│   └── utils.py              # Common utility functions
│
├── creator_discovery/         # Creator search and recommendation
│   ├── models/               # AI models for embeddings and search
│   ├── schemas/              # Pydantic models for API
│   ├── services/             # Business logic
│   └── main.py               # FastAPI application
│
├── ai_communication/          # AI-powered communication
│   ├── models/               # Gemini client and negotiation agent
│   ├── schemas/              # Communication API schemas
│   ├── services/             # Outreach and negotiation services
│   └── main.py               # FastAPI application
│
├── contract_automation/       # Legal document generation
├── analytics_engine/          # Performance analytics
├── api_gateway/              # Main API orchestration
└── docker-compose.yml        # Complete system deployment
```

## 🚀 Next Steps for Hackathon

### Immediate Integration

1. **Frontend Integration**: Connect your React/Next.js frontend to `http://localhost:8000`
2. **Authentication**: Implement JWT tokens through the API Gateway
3. **Real-time Updates**: Use WebSocket connections for live campaign status
4. **File Uploads**: Enable campaign asset uploads through the media endpoints

### Demo Scenarios

1. **Fitness Brand Campaign**: 
   - Search: "fitness influencers with high engagement"
   - Generate outreach for top 3 creators
   - Simulate negotiation process
   - Generate contracts

2. **Tech Product Launch**:
   - Search: "tech reviewers and gadget enthusiasts"  
   - Batch outreach generation
   - Performance analytics preview

## 📝 License

This project is developed for the hackathon. Please check individual API terms of service for Google Gemini and other integrated services.