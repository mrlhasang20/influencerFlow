# InfluencerFlow

An AI-powered influencer marketing platform that automates creator discovery, outreach, and contract management.

## Features

- **Creator Discovery**: Find relevant influencers based on your campaign needs
- **AI Communication**: Generate personalized outreach messages
- **Contract Automation**: Create and manage influencer contracts
- **API Gateway**: Unified interface for all services

## Project Structure

```
influencerFlow/
├── backend/
│   ├── ai_services/
│   │   ├── api_gateway/        # Main API entry point
│   │   ├── creator_discovery/  # Influencer search service
│   │   ├── ai_communication/   # Message generation service
│   │   └── contract_automation/# Contract management service
│   └── requirements.txt
├── frontend/                   # React frontend (coming soon)
└── README.md
```

## Setup

1. Clone the repository
2. Set up Python virtual environment:
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create `.env` file in `backend/ai_services/` directory
   - Add required environment variables (see `.env.example`)

4. Start the services:
   ```bash
   # Start API Gateway (starts all services)
   python backend/ai_services/api_gateway/main.py
   ```

## API Documentation

- API Gateway: http://localhost:8000
- Creator Discovery: http://localhost:8001
- AI Communication: http://localhost:8002
- Contract Automation: http://localhost:8003

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

MIT License