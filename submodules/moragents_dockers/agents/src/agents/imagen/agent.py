import base64
import logging
from io import BytesIO

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.models.messages import ChatRequest

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ImagenAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm
        self.embeddings = embeddings

    def _setup_headless_browser(self):
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

    def _generate_with_fluxai(self, prompt):
        logger.info(f"Attempting image generation for prompt: {prompt}")
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
                EC.presence_of_element_located(
                    (By.XPATH, "//img[@alt='Generated' and @loading='lazy']")
                )
            )

            if img_element:
                img_src = img_element.get_attribute("src")
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
                        logger.error(
                            f"Failed to download image. Status code: {response.status_code}"
                        )
                else:
                    logger.warning(
                        "Image format not supported. Expected a valid imgproxy or replicate URL."
                    )
            else:
                logger.warning(
                    "Image not found or still generating. You may need to increase the wait time."
                )

        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            return None
        finally:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

    def _encode_image(self, image):
        if image:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        return None

    def generate_image(self, prompt):
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

    def chat(self, request: ChatRequest):
        try:
            data = request.dict()
            logger.info(f"Received chat request: {data}")
            if "prompt" in data:
                prompt = data["prompt"]
                result = self.generate_image(prompt["content"])
                return {"role": "assistant", "content": result}
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {"error": "Missing parameters"}, 400
        except Exception as e:
            logger.error(f"Unexpected error in chat method: {str(e)}, request: {request}")
            raise e
