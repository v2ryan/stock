import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Function to fetch historical data
def fetch_data(stock_code):
    try:
        data = yf.download(stock_code, period='3y', interval='1d')
        if data.empty:
            raise ValueError("No data found for this stock code.")
        return data
    except Exception as e:
        raise ValueError(f"Error fetching data: {str(e)}")

# Function to calculate indicators
def calculate_indicators(data):
    # RSI
    data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()

    # ATR
    data['ATR'] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()

    # MACD
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()

    # Stochastic Oscillator
    stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
    data['%K'] = stoch.stoch()
    data['%D'] = stoch.stoch_signal()

    return data

# Streamlit app layout
st.title("Stock Analysis App")

# User input for stock code
stock_code = st.text_input("Enter Stock Code (e.g., AAPL for US or 0005.HK for HK):")

if stock_code:
    # Fetch and display historical data
    try:
        data = fetch_data(stock_code)
        
        st.write(f"Historical Data for {stock_code}:")
        st.line_chart(data['Close'])

        # Calculate indicators
        data_with_indicators = calculate_indicators(data)

        # Display indicators
        st.write("Indicators:")
        st.line_chart(data_with_indicators[['RSI', 'ATR', 'MACD', '%K', '%D']])

        # Buy/Sell suggestion based on simple rules (this can be improved)
        if (data_with_indicators['RSI'].iloc[-1] < 30) and (data_with_indicators['MACD'].iloc[-1] > data_with_indicators['MACD_Signal'].iloc[-1]):
            st.write("Suggestion: Buy")
        elif (data_with_indicators['RSI'].iloc[-1] > 70) and (data_with_indicators['MACD'].iloc[-1] < data_with_indicators['MACD_Signal'].iloc[-1]):
            st.write("Suggestion: Sell")
        else:
            st.write("Suggestion: Hold")

    except ValueError as e:
        st.error(str(e))
