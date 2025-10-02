# Healthcare Chatbot

A complete, production-ready healthcare chatbot built with Rasa, FastAPI, React, and Docker.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM available
- Ports 3000, 5005, 5055, 8000 available

### 1. Clone & Setup
```bash
git clone <your-repo>
cd healthcare-chatbot
```

### 2. Build & Run
```bash
cd docker
docker-compose up --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Rasa Core**: http://localhost:5005
- **Rasa Actions**: http://localhost:5055

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend       │◄──►│   Rasa NLU      │
│   (React)       │    │   (FastAPI)     │    │   (Actions)     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5005    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

- **Symptom Triage**: AI-powered assessment and urgency classification
- **Appointment Booking**: Complete scheduling system with form validation
- **Health Advice**: Evidence-based recommendations
- **Emergency Detection**: Automatic escalation for critical symptoms
- **Real-time Chat**: WebSocket communication with typing indicators
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development  
```bash
cd frontend
npm install
npm run dev
```

### Rasa Development
```bash
cd rasa
pip install -r requirements.txt
rasa train
rasa run --enable-api --cors "*"
```

## 📦 Production Deployment

### Using Production Docker Compose
```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
Copy `.env.example` files and configure:
- `backend/.env.example` → `backend/.env`
- `frontend/.env.example` → `frontend/.env`
- `docker/.env.example` → `docker/.env`

## 🧪 Testing

### Test the System
```bash
# Test backend
curl http://localhost:8000/health

# Test Rasa
curl http://localhost:5005/status

# Test WebSocket (requires wscat)
wscat -c ws://localhost:8000/ws/chat/test_session
```

## 🏥 Healthcare Features

### Symptom Assessment
- Emergency detection (chest pain, breathing difficulty)
- Urgency classification (low, medium, high, emergency)
- Triage recommendations
- Automatic healthcare provider referral

### Appointment System
- Patient information collection
- Schedule validation
- Booking confirmation
- Cancellation handling

### Safety Features
- Emergency response protocols
- Human handover capabilities
- Medical disclaimer compliance
- HIPAA-ready architecture

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Build failures**: Run `docker-compose build --no-cache`
3. **Rasa path errors**: Ensure all Dockerfile paths are correct
4. **Connection issues**: Check that all services are running

### Logs
```bash
docker-compose logs -f backend
docker-compose logs -f rasa-core
docker-compose logs -f frontend
```

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Medical Disclaimer

This chatbot provides general health information and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.
