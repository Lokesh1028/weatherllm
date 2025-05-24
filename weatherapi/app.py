import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize API keys
OPENWEATHER_API_KEY = "ecd6fc0f11cb6c567fb66f33536efcb7"
GROQ_API_KEY = "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"

# Check if API keys are available
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found!")
    st.info("Please set your GROQ_API_KEY in a .env file. Get your API key from: https://console.groq.com/")
    st.code("GROQ_API_KEY=your_groq_api_key_here")
    st.stop()

if not OPENWEATHER_API_KEY:
    st.error("❌ OPENWEATHER_API_KEY not found!")
    st.info("Please set your OPENWEATHER_API_KEY in a .env file. Get your API key from: https://openweathermap.org/api")
    st.code("OPENWEATHER_API_KEY=your_openweather_api_key_here")
    st.stop()

# Initialize Groq client
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Error initializing Groq client: {str(e)}")
    st.stop()

def get_current_weather(location):
    """Get current weather data from OpenWeather API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "location": location,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "feels_like": data["main"]["feels_like"]
        }
        
        return json.dumps(weather_info)
        
    except requests.exceptions.RequestException as e:
        error_info = {
            "location": location,
            "error": f"Could not fetch weather data: {str(e)}"
        }
        return json.dumps(error_info)

# Define the function schema for Groq
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location to help determine if it's suitable to go outside",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. London, New York, Tokyo",
                    }
                },
                "required": ["location"],
            },
        },   
    }
]

def chat_with_groq(user_message, chat_history):
    """Handle chat with Groq including function calling"""
    
    # Prepare messages for the conversation
    messages = [
        {
            "role": "system",
            "content": """You are a helpful weather assistant. When users ask about weather in a specific location, use the get_current_weather function to fetch real-time weather data.

After getting weather data, provide helpful recommendations about:
- Whether it's suitable to go outside
- What activities are good for the weather
- What to wear or bring
- Any weather-related precautions

Be conversational, friendly, and give practical advice based on the actual weather conditions."""
        }
    ]
    
    # Add chat history
    for msg in chat_history:
        messages.append(msg)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Make the initial request with function calling
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=500
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to call a function
        if response_message.tool_calls:
            # Get the function call details
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the weather function
            if function_name == "get_current_weather":
                weather_data = get_current_weather(**function_args)
                
                # Add the function call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": weather_data
                })
                
                # Make a second request to get the final response
                final_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                return final_response.choices[0].message.content, json.loads(weather_data)
        
        # If no function call, return the direct response
        return response_message.content, None
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}", None

def display_weather_metrics(weather_data):
    """Display weather data in a nice format"""
    if weather_data and "error" not in weather_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌡️ Temperature", f"{weather_data['temperature']}°C")
            st.metric("🤗 Feels Like", f"{weather_data['feels_like']}°C")
        
        with col2:
            st.metric("💧 Humidity", f"{weather_data['humidity']}%")
            st.metric("🌬️ Wind Speed", f"{weather_data['wind_speed']} m/s")
        
        with col3:
            st.metric("🌤️ Conditions", weather_data['description'].title())
            st.metric("📍 Location", weather_data['location'])

def main():
    st.title("🌤️ Weather Chat Assistant")
    st.write("Ask me about the weather in any city and I'll help you decide if it's good to go outside!")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display weather data if available
            if "weather_data" in message and message["weather_data"]:
                with st.expander("📊 Weather Details"):
                    display_weather_metrics(message["weather_data"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about weather in any city..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Getting weather info..."):
                # Prepare chat history for API call
                chat_history = [{"role": msg["role"], "content": msg["content"]} 
                              for msg in st.session_state.messages[:-1]]  # Exclude current message
                
                response, weather_data = chat_with_groq(prompt, chat_history)
                
                # Display response
                st.write(response)
                
                # Display weather data if available
                if weather_data:
                    with st.expander("📊 Weather Details", expanded=True):
                        display_weather_metrics(weather_data)
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "weather_data": weather_data
                })
    
    # Clear chat button in sidebar
    with st.sidebar:
        st.title("Options")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Example questions:")
        st.markdown("- What's the weather like in Paris?")
        st.markdown("- Should I go hiking in Denver today?")
        st.markdown("- Is it good weather for a picnic in Tokyo?")
        st.markdown("- Do I need an umbrella in London?")

if __name__ == "__main__":
    main() 