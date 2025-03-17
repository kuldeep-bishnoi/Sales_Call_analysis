# Sales Call Analysis System

A comprehensive system for transcribing, analyzing, and evaluating sales calls to provide actionable insights into customer interactions.

## Features

- **Audio Preprocessing**: Clean and enhance audio quality before analysis
- **Speech-to-Text**: Transcribe sales calls with high accuracy using OpenAI Whisper
- **Sentiment Analysis**: Determine the emotional tone of conversations
- **Engagement Analysis**: Measure customer interest and response patterns
- **Objection Detection**: Identify and categorize customer objections
- **Conversion Probability**: Predict how likely a customer is to convert
- **Interactive Dashboard**: Visualize insights with a user-friendly Streamlit interface

## System Architecture

The system follows a modular architecture:

1. **Core Components**:
   - Audio preprocessing for cleaning recordings
   - Speech-to-text transcription using Whisper
   - Text processing and cleaning

2. **Analysis Services**:
   - Sentiment analyzer to detect conversation tone
   - Engagement analyzer to measure customer interest
   - Objection detector to identify customer concerns
   - Satisfaction and conversion probability analyzer

3. **API and Frontend**:
   - FastAPI backend for handling requests
   - MongoDB database for storing results
   - Streamlit dashboard for visualizing insights

## Prerequisites

- Python 3.8+
- MongoDB
- Whisper.cpp model file (automatically downloaded during setup)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sales-call-analysis.git
   cd sales-call-analysis
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file if you need to change default settings.

5. Download the Whisper model:
   ```
   python utils/download_whisper_model.py
   ```
   This will download the base English model by default. For other models, use the `--model` option:
   ```
   python utils/download_whisper_model.py --model medium
   ```
   Available models: tiny, base, small, medium, large, large-v1, large-v2, large-v3

6. Make sure MongoDB is running on your system.

## Usage

### Starting the API Server

Run the FastAPI server:

```
python main.py
```

The API server will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

### Starting the Dashboard

Run the Streamlit dashboard:

```
python run_streamlit.py
```

The dashboard will be available at `http://localhost:8501`.

### Using the System

1. **Upload a Sales Call Recording**:
   - Go to the dashboard at `http://localhost:8501`
   - Use the upload form in the sidebar to upload an audio file (MP3, WAV, FLAC, or M4A)
   - Check "Auto-process after upload" to automatically start processing

2. **View Analysis Results**:
   - Navigate to the Dashboard page
   - Select a processed call from the dropdown
   - Explore sentiment, engagement, objections, and conversion probability
   - Review key insights and the full transcript

3. **API Integration**:
   - Upload calls: `POST /api/upload`
   - Process calls: `POST /api/process/{call_id}`
   - Get results: `GET /api/calls/{call_id}`

## Development

### Project Structure

```
sales-call-analysis/
├── app/
│   ├── api/              # FastAPI routes and app
│   ├── analysis/         # Analysis modules
│   ├── core/             # Core functionality
│   ├── database/         # Database connections and repositories
│   ├── frontend/         # Streamlit dashboard
│   ├── models/           # Data models
│   ├── preprocessing/    # Audio preprocessing
│   ├── utils/            # Utility functions
│   └── config/           # Configuration settings
├── data/                 # Data storage directories
├── .env.example          # Example environment variables
├── main.py               # API server entry point
├── requirements.txt      # Project dependencies
├── run_streamlit.py      # Dashboard entry point
└── README.md             # This file
```

### Running Tests

```
# Coming soon
```

## Future Enhancements

- Real-time analysis of live calls
- AI-based coaching and recommendations
- Integration with popular CRM systems
- Speaker diarization for distinguishing between sales rep and customer
- Advanced analytics and trend reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the Whisper and GPT-4 models
- FastAPI and Streamlit for making awesome development frameworks

