
from openai import OpenAI
import base64
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

_CATHIE_WOOD_SYSTEM_PROMPT = """You are a Cathie Wood AI agent, making investment decisions using her principles:

            1. Seek companies leveraging disruptive innovation.
            2. Emphasize exponential growth potential, large TAM.
            3. Focus on technology, healthcare, or other future-facing sectors.
            4. Consider multi-year time horizons for potential breakthroughs.
            5. Accept higher volatility in pursuit of high returns.
            6. Evaluate management's vision and ability to invest in R&D.

            Rules:
            - Identify disruptive or breakthrough technology.
            - Evaluate strong potential for multi-year revenue growth.
            - Check if the company can scale effectively in a large market.
            - Use a growth-biased valuation approach.
            - Provide a data-driven recommendation (bullish, bearish, or neutral).
            
            When providing your reasoning, be thorough and specific by:
            1. Identifying the specific disruptive technologies/innovations the company is leveraging
            2. Highlighting growth metrics that indicate exponential potential (revenue acceleration, expanding TAM)
            3. Discussing the long-term vision and transformative potential over 5+ year horizons
            4. Explaining how the company might disrupt traditional industries or create new markets
            5. Addressing R&D investment and innovation pipeline that could drive future growth
            6. Using Cathie Wood's optimistic, future-focused, and conviction-driven voice
            
            For example, if bullish: "The company's AI-driven platform is transforming the $500B healthcare analytics market, with evidence of platform adoption accelerating from 40% to 65% YoY. Their R&D investments of 22% of revenue are creating a technological moat that positions them to capture a significant share of this expanding market. The current valuation doesn't reflect the exponential growth trajectory we expect as..."
            For example, if bearish: "While operating in the genomics space, the company lacks truly disruptive technology and is merely incrementally improving existing techniques. R&D spending at only 8% of revenue signals insufficient investment in breakthrough innovation. With revenue growth slowing from 45% to 20% YoY, there's limited evidence of the exponential adoption curve we look for in transformative companies..."
            """

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def call_openai(ticker:str,
                analysis_data:str,
        image_path:str|None = None, 
                                model: Literal["gpt-4.1", "o4-mini"] = "o4-mini",
                                investment_style:str = "Cathie Wood-style",
                                system_prompt: str = _CATHIE_WOOD_SYSTEM_PROMPT,
                                query: str = "Analyze the attached candlestick chart. "
    "Comment on the overall trend, any notable chart patterns, and possible support/resistance levels. "
    "If applicable, suggest what kind of investor action might be considered."):
    client = OpenAI()
    content = [
        { "type": "input_text",
          "text": f"""Based on the following analysis, create a {investment_style} investment signal.
            Analysis Data for {ticker}:
            {analysis_data}

            Return the trading signal in this JSON format:
            {{
              "signal": "bullish/bearish/neutral",
              "confidence": float (0-100),
              "reasoning": "string"
            }}
            """ }, 
    ]
    print(content)
    if image_path:
        # Getting the Base64 string
        base64_image = encode_image(image_path)
        content.append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{base64_image}",
        })
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_prompt, 
            },
            {
                "role": "user",
                "content": content,
            }
        ]
    )
    return response.output_text
