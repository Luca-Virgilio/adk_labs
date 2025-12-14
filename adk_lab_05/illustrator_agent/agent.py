import os
import uuid
from dotenv import load_dotenv

# ADK imports
from google.adk import Agent
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext

from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from google import genai
from google.genai.types import GenerateContentConfig, ImageConfig
# from google.cloud import storage  # commented out for local operation

load_dotenv()

# --- SDK Initialization (local) ---
# NOTE: Cloud project/bucket settings are commented out for local operation.
# project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
# location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
client = genai.Client()


def generate_image(prompt: str) -> dict[str, str]:
    """Generate an illustration locally using Gemini and save it to ./generated-images.
 
    Args:
        prompt (str): The prompt to provide to the image generation model.
 
    Returns:
        dict[str, str]: {"image_url": "file://<absolute_path_to_generated_image>"}
    """
    # 1. Call the model
    response = client.models.generate_content(
        model=os.getenv("IMAGE_MODEL"),
        contents=prompt,
        config=GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=ImageConfig(
                aspect_ratio="1:1",
            ),
            candidate_count=1,
        ),
    )
 
    # 2. Extract the raw image data from the response
    image_bytes = response.candidates[0].content.parts[0].inline_data.data
    """"
    # 3. Upload the image bytes to Google Cloud Storage
    storage_client = storage.Client(project=project_id)
    bucket_name = f"{project_id}-bucket" # Your bucket name
    bucket = storage_client.bucket(bucket_name)
    
    # Generate a unique name for the image file
    blob_name = f"generated-images/{uuid.uuid4()}.png"
    blob = bucket.blob(blob_name)
    
    # Upload the data
    blob.upload_from_string(image_bytes, content_type="image/png")

    # 4. Construct and return the public URL
    url = f"https://storage.cloud.google.com/{bucket_name}/{blob_name}"
    
    return {"image_url": url}
    """
 
    # 3. Save the image bytes to a local directory
    out_dir = os.path.join(os.getcwd(), "generated-images")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.png"
    file_path = os.path.join(out_dir, filename)
    # Write bytes to file
    with open(file_path, "wb") as f:
        f.write(image_bytes)
 
    # 4. Return a local file URL
    return {"image_url": f"file://{file_path}"}


# ==============================================================================
# Agent code
# ==============================================================================
root_agent = Agent(
    name="illustration_agent",
    model=os.getenv("MODEL"),
    description="Creates branded illustrations.",
    instruction="""
    You are an illustrator for a stadium maintenance company.

    You will receive a block of text, it is your job to write
    a prompt that will express the ideas of this text.

    You always emphasize that there should be no text in the image.
    You prefer a flat, geometric, corporate memphis diagrammatic style of art.
    Your brand palette is purple (#BF40BF), green (#DAF7A6), and sunset colors.
    Consider a clever or charming approach with specific details.
    Incorporate stadium imagery like lights, yardage indicators, green fields, popcorn.
    Incorporate maintenance imagery like wrenches, toolboxes, overalls.
    Incorporate general sports imagery like balls, caps, gloves.

    Once you have written the prompt, use your 'generate_image' tool to generate an image.
    Always return both of the following:
        - the text of the prompt you used
        - the generated image URL returned by your tool
    """,
    tools=[generate_image]
)
