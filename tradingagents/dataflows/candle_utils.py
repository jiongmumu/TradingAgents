import mplfinance as mpf
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import yfinance as yf
from openai import OpenAI
import base64
from typing import Literal
import alpha_vantage_utils

def save_ticker_1y_candle(symbol:str, path: str=None, dpi=100):
    if path is None:
        path = f'{symbol}_candle.png'
    data = yf.download(symbol, period="1y", interval="1d", multi_level_index=False)
    data=alpha_vantage_utils.AlphaVantageClient().add_eps_column(data, 'META')
    data['pe'] = data['Close']/data['eps']
    ap_pe = mpf.make_addplot(data['pe'], panel=2, color='purple', type='line', ylabel='PE')
    fig, axes =mpf.plot(data, type='candle', style='charles', volume=True,
            datetime_format='%Y-%m-%d',
            xrotation=45,
            addplot=[ap_pe],
            title=symbol,
            #tight_layout=True,
            update_width_config=dict(candle_linewidth=0.7),
            returnfig=True,
            figsize=(30, 10))
    # Step 3: Access and modify the x-axis ticks (first axes is price plot)
    ax = axes[0]
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Show every 3 days
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # Optional: Improve layout
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.show()

def interactive_candle(symbol:str):
    data = yf.download(symbol, period="1y", interval="1d", multi_level_index=False)
    # it can zoom in, zoom out, better for interactive support.
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    return fig.update_layout(xaxis_rangeslider_visible=False)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def call_openai_with_image_path(image_path:str, 
                                model: Literal["gpt-4.1", "o4-mini"],
                                query: str = "Is now the right time to buy the stock?"):
    client = OpenAI()
    # Getting the Base64 string
    base64_image = encode_image(image_path)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": query },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )
    return response.output_text