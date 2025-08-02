
from openai import OpenAI
import base64
from typing import Literal

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def call_openai_with_image_path(image_path:str, 
                                model: Literal["gpt-4.1", "o4-mini"] = "o4-mini",
                                query: str = "Analyze the attached candlestick chart. "
    "Comment on the overall trend, any notable chart patterns, and possible support/resistance levels. "
    "If applicable, suggest what kind of investor action might be considered."):
    client = OpenAI()
    # Getting the Base64 string
    base64_image = encode_image(image_path)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a professional financial assistant that replies in Markdown format."
                    "You have a lot of expertise in technical analysis. "
                    "Your role is to analyze stock candlestick charts and help investors make informed decisions. "
                    "Identify patterns, support and resistance levels, potential breakouts, and trend direction. "
                    "Provide clear and concise analysis, avoid speculation, and explain your reasoning briefly and professionally."
                )
            },
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": query },  # e.g., "Analyze this chart and suggest potential actions." or more specific
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    )
    return response.output_text

MULTI_EARNINGS_CALL_SUMMARY_PROMPT = '''
Can you summarize 2023, 2024 2025  each quarter per sector growth(if any),  revenue, eps growth in one table?
Is there any sector is becoming more important each year?
'''

def call_openai_with_transcript(transcript: str,
                                model: Literal["gpt-4.1", "o4-mini"] = "o4-mini",
                                query: str = "Identify key takeaways from the earnings call and list any red flags or positive signals."):
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "You are a helpful financial assistant that replies in Markdown format. You are good at summarizing earnings call transcript and identify potential highlights or issues.",
            },
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": query },
                    {
                        "type": "input_text",
                        "text": transcript,
                    },
                ],
            }
        ],
    )
    return response.output_text

def call_openai_with_img_transcript(image_path:str, 
                                    transcript: str,
                                model: Literal["gpt-4.1", "o4-mini"] = "o4-mini",
                                query: str = "Answer with Yes/No whether you think should buy the stock. "
                                "Then follow with confidence level 0-100 how confident you are about the decision."
                                "Explain the reason, summarize key takeaways from earnings call, use the provided transcript and candle graph info."):
    client = OpenAI()
    # Getting the Base64 string
    base64_image = encode_image(image_path)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a professional financial assistant with expertise in both technical analysis and fundamental analysis. "
                    "Your role is to analyze stock candlestick charts, transcript and help investors make informed decisions. "
                    "For the transcript, identify key takeaways from the earnings call and list any red flags or positive signals."
                )
            },
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": query }, 
                    {
                        "type": "input_text",
                        "text": transcript,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    )
    return response.output_text
