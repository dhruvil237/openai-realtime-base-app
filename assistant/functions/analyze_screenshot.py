import base64
import pyautogui
from openai import OpenAI
from ...config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


async def take_and_analyze_screenshot(user_query: str) -> str:
    """
    Analyze the contents of a screenshot and provide a detailed answer/solution based on the user query.

    Args:
        user_query (str): The user query to be used in the conversation.

    Returns:
        str: The result of the analysis of the screenshot.
    """

    # Take a screenshot and save it to a temporary file
    screenshot = pyautogui.screenshot()
    screenshot_path = "temp_screenshot.png"
    screenshot.save(screenshot_path)

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    # Getting the base64 string
    base64_image = encode_image(screenshot_path)

    system_prompt = "You are an expert at debugging issues by analysing screenshots. Analyze the contents of the screenshot and provide a brief and accurate answer/solution based on the user query."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
    )

    result = response.choices[0].message.content
    return f"Screenshot Analysis Result: {result}"
