import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Function to fetch historical data
def fetch_data(stock_code):
    try:
        # Fetching data from Yahoo Finance
        data = yf.download(stock_code, period='3y', interval='1d')
        print(data)  # Debugging line to check fetched data
        
        # Check if the data is empty
        if data.empty:
            raise ValueError("No data found for this stock code.")
        
        return data
    except ValueError as ve:
        raise ve  # Raise specific ValueError
    except Exception as e:
        raise RuntimeError(f"Error fetching data: {str(e)}")

# Function to calculate indicators
def calculate_indicators(data):
    # RSI
    rsi = ta.momentum.RSIIndicator(data['Close'])
    data['RSI'] = rsi.rsi()

    # ATR
    atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'])
    data['ATR'] = atr.average_true_range()

    # MACD
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()

    # Stochastic Oscillator
    stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
    data['%K'] = stoch.stoch()
    data['%D'] = stoch.stoch_signal()

    # Drop NaN values that may arise from indicator calculations
    return data.dropna()

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
        last_rsi = data_with_indicators['RSI'].iloc[-1]
        last_macd = data_with_indicators['MACD'].iloc[-1]
        last_macd_signal = data_with_indicators['MACD_Signal'].iloc[-1]

        if (last_rsi < 30) and (last_macd > last_macd_signal):
            st.write("Suggestion: Buy")
        elif (last_rsi > 70) and (last_macd < last_macd_signal):
            st.write("Suggestion: Sell")
        else:
            st.write("Suggestion: Hold")

    except ValueError as e:
        st.error(str(e))
    except RuntimeError as e:
        st.error(str(e))
