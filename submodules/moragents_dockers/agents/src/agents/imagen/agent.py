import base64
import logging
from io import BytesIO
from typing import Dict, Any, List, Optional

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class ImagenAgent(AgentCore):
    """Agent for handling image generation requests."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided: List[str] = []  # No tools needed for image generation
        self.tool_bound_llm = self.llm

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for image generation."""
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an image generation assistant. "
                        "Help users create images by understanding their prompts "
                        "and generating appropriate images."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            # For image generation, we'll directly use the prompt content
            result = self.generate_image(request.prompt.content)

            if result["success"]:
                return AgentResponse.success(
                    content="Image generated successfully",
                    metadata={"success": True, "service": result["service"], "image": result["image"]},
                )
            else:
                return AgentResponse.error(error_message=result["error"])

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Image generation agent doesn't use tools."""
        return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

    def _setup_headless_browser(self) -> webdriver.Chrome:
        chrome_options = Options()

        # Essential Chromium flags for running in Docker
        chrome_options.binary_location = "/usr/bin/chromium"
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")

        # Additional options for stability
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--disable-software-rasterizer")

        try:
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chromium browser: {str(e)}")
            raise

    def _generate_with_fluxai(self, prompt: str) -> Optional[Image.Image]:
        logger.info(f"Attempting image generation for prompt: {prompt}")
        driver = None
        try:
            driver = self._setup_headless_browser()
            driver.set_page_load_timeout(30)
            driver.get("https://fluxai.pro/fast-flux")

            # Find textarea and enter the prompt
            wait = WebDriverWait(driver, 30)
            textarea = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            textarea.clear()
            textarea.send_keys(prompt)

            # Click generate button
            run_button = driver.find_element(
                By.XPATH,
                "//textarea/following-sibling::button[contains(text(), 'Generate')]",
            )
            run_button.click()

            # Wait for the generated image
            img_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//img[@alt='Generated' and @loading='lazy']"))
            )

            if img_element:
                img_src = img_element.get_attribute("src")
                if not img_src:
                    logger.warning("Image source URL is empty")
                    return None

                logger.debug(f"Image source: {img_src}")

                # Download the image
                if img_src.startswith(
                    (
                        "https://api.together.ai/imgproxy/",
                        "https://fast-flux-demo.replicate.workers.dev/api/generate-image",
                    )
                ):
                    response = requests.get(img_src)
                    if response.status_code == 200:
                        img_data = response.content
                        return Image.open(BytesIO(img_data))
                    else:
                        logger.error(f"Failed to download image. Status code: {response.status_code}")
                else:
                    logger.warning("Image format not supported. Expected a valid imgproxy or replicate URL.")
            else:
                logger.warning("Image not found or still generating. You may need to increase the wait time.")

        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")

        return None

    def _encode_image(self, image: Optional[Image.Image]) -> Optional[str]:
        if image:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        return None

    def generate_image(self, prompt: str) -> Dict[str, Any]:
        logger.info(f"Starting image generation for prompt: {prompt}")

        # Generate image using the new method
        image = self._generate_with_fluxai(prompt)
        if image:
            img_str = self._encode_image(image)
            if img_str:
                return {"success": True, "service": "FluxAI", "image": img_str}

        return {
            "success": False,
            "error": "Failed to generate image with FluxAI",
        }
