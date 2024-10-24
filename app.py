import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.trend import MACD

# Function to calculate technical indicators
def calculate_indicators(data):
    # Drop rows with NaN values in 'Close'
    data = data.dropna(subset=['Close'])
    
    if len(data) < 14:
        st.warning("Not enough data points for RSI calculation.")
        return data

    # Calculate RSI
    rsi_indicator = RSIIndicator(close=data['Close'])
    data['RSI'] = rsi_indicator.rsi()

    # Calculate ATR
    atr_indicator = AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'])
    data['ATR'] = atr_indicator.average_true_range()

    # Calculate MACD
    macd_indicator = MACD(close=data['Close'])
    data['MACD'] = macd_indicator.macd()
    data['MACD_Signal'] = macd_indicator.macd_signal()

    return data

# Streamlit app layout
st.title('Stock Analysis App')

# User inputs for stock codes
stock_code = st.text_input("Enter Stock Code (e.g., AAPL for Apple or 0005.HK for HSBC):")

if stock_code:
    # Fetch historical data for the last three years
    try:
        data = yf.download(stock_code, start="2021-01-01", end="2024-01-01")
        if data.empty:
            st.warning("No data found for the provided stock code.")
        else:
            st.write(data)

            # Calculate indicators
            data_with_indicators = calculate_indicators(data)

            # Display the indicators and plots
            st.subheader('Technical Indicators')
            st.line_chart(data_with_indicators[['Close', 'RSI', 'ATR', 'MACD']])

            # Buy/Sell Signal Logic
            buy_signal = (data_with_indicators['RSI'] < 30) & (data_with_indicators['MACD'] > data_with_indicators['MACD_Signal'])
            sell_signal = (data_with_indicators['RSI'] > 70) & (data_with_indicators['MACD'] < data_with_indicators['MACD_Signal'])

            if buy_signal.any():
                st.success("Buy Signal Detected!")
            
            if sell_signal.any():
                st.warning("Sell Signal Detected!")

            # Display the RSI chart
            st.subheader('RSI Chart')
            plt.figure(figsize=(10, 4))
            plt.plot(data_with_indicators.index, data_with_indicators['RSI'], label='RSI', color='blue')
            plt.axhline(30, linestyle='--', alpha=0.5, color='red')
            plt.axhline(70, linestyle='--', alpha=0.5, color='green')
            plt.title('Relative Strength Index (RSI)')
            plt.legend()
            st.pyplot(plt)

            # Display the MACD chart
            st.subheader('MACD Chart')
            plt.figure(figsize=(10, 4))
            plt.plot(data_with_indicators.index, data_with_indicators['MACD'], label='MACD', color='orange')
            plt.plot(data_with_indicators.index, data_with_indicators['MACD_Signal'], label='Signal Line', color='green')
            plt.title('Moving Average Convergence Divergence (MACD)')
            plt.legend()
            st.pyplot(plt)

# Run the app using: streamlit run app.py
