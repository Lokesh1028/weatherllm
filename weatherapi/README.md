# Weather Chat Assistant

A Streamlit chat application that uses Groq's function calling to fetch real-time weather data and provide personalized recommendations about whether it's suitable to go outside.

## Features

- 🌤️ **Real-time Weather Data**: Fetches current weather from OpenWeather API
- 🤖 **AI Function Calling**: Groq AI automatically calls weather API when needed
- 💬 **Chat Interface**: Natural conversation with persistent chat history
- 📊 **Beautiful Weather Display**: Detailed weather metrics with emojis
- 🎯 **Smart Recommendations**: AI analyzes weather to suggest activities and precautions

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get API Keys:**
   - **OpenWeather API**: Sign up at https://openweathermap.org/api (Free)
   - **Groq API**: Sign up at https://console.groq.com/ (Free)

3. **Create `.env` file in project root:**
   ```
   OPENWEATHER_API_KEY=your_actual_openweather_key
   GROQ_API_KEY=your_actual_groq_key
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## How It Works

1. **User asks about weather** in natural language
2. **Groq AI detects weather request** and automatically calls the weather function
3. **Real weather data is fetched** from OpenWeather API
4. **AI provides recommendations** based on actual weather conditions
5. **Weather details displayed** in expandable metrics

## Example Conversations

- "What's the weather like in Paris?"
- "Should I go hiking in Denver today?"
- "Is it good weather for a picnic in Tokyo?"
- "Do I need an umbrella in London?"
- "What should I wear outside in New York?"

## Technical Implementation

- **Groq Function Calling**: Uses `tools` parameter with proper function schema
- **Error Handling**: Graceful handling of API failures and invalid cities
- **Session State**: Persistent chat history across interactions
- **Weather Metrics**: Temperature, humidity, wind speed, and conditions
- **Responsive UI**: Clean chat interface with sidebar options 