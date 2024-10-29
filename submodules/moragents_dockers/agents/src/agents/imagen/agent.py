import logging
import time
import base64
import requests

from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _generate_with_fastflux(self, prompt):
        logger.info(f"Attempting FastFlux generation for prompt: {prompt}")
        try:
            driver = self._setup_headless_browser()
        except Exception as e:
            logger.error(f"Failed to setup Chrome browser: {str(e)}")
            return None

        try:
            driver.get("https://www.fastflux.ai/")
            time.sleep(3)

            textarea = driver.find_element(By.TAG_NAME, "textarea")
            img_div = driver.find_element(By.CSS_SELECTOR, "div.aspect-square")
            initial_style = img_div.get_attribute("style")

            textarea.clear()
            textarea.send_keys(prompt)
            driver.find_element(By.TAG_NAME, "button").click()

            WebDriverWait(driver, 30).until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "div.aspect-square"
                ).get_attribute("style")
                != initial_style
            )

            img_div = driver.find_element(By.CSS_SELECTOR, "div.aspect-square")
            style = img_div.get_attribute("style")
            url_data = style.split('background-image: url("')[1].split('")')[0]

            if url_data == "undefined":
                logger.warning("FastFlux generation failed - undefined result")
                return None

            if url_data.startswith("data:image"):
                _, encoded = url_data.split(",", 1)
                img_data = base64.b64decode(encoded)
                return Image.open(BytesIO(img_data))

            logger.warning("FastFlux generation failed - unsupported format")
            return None

        except Exception as e:
            logger.error(f"Error in FastFlux generation: {str(e)}")
            return None
        finally:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

    def _generate_with_magicstudio(self, prompt):
        logger.info(f"Attempting MagicStudio generation for prompt: {prompt}")
        try:
            driver = self._setup_headless_browser()
        except Exception as e:
            logger.error(f"Failed to setup Chrome browser: {str(e)}")
            return None

        try:
            driver.get("https://magicstudio.com/ai-art-generator/")

            textarea = driver.find_element(By.ID, "description")
            img_element = driver.find_element(
                By.CSS_SELECTOR, "img.rounded-xl[alt='generated image']"
            )
            initial_src = img_element.get_attribute("src")

            textarea.clear()
            textarea.send_keys(prompt)

            prompt_box = driver.find_element(By.ID, "prompt-box")
            submit_button = prompt_box.find_element(By.TAG_NAME, "button")
            submit_button.click()

            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "img.rounded-xl[alt='generated image']"
                ).get_attribute("src")
                != initial_src
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            img_tag = soup.find("img", class_="rounded-xl", alt="generated image")

            if img_tag and "src" in img_tag.attrs:
                if img_tag["src"].startswith("data:image"):
                    _, encoded = img_tag["src"].split(",", 1)
                    img_data = base64.b64decode(encoded)
                    return Image.open(BytesIO(img_data))
                else:
                    response = requests.get(img_tag["src"])
                    return Image.open(BytesIO(response.content))

            logger.warning("MagicStudio generation failed - image not found")
            return None

        except Exception as e:
            logger.error(f"Error in MagicStudio generation: {str(e)}")
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

        # Try FastFlux first
        image = self._generate_with_fastflux(prompt)
        if image:
            img_str = self._encode_image(image)
            if img_str:
                return {"success": True, "service": "FastFlux", "image": img_str}

        # Fallback to MagicStudio
        logger.info("FastFlux failed, attempting MagicStudio")
        image = self._generate_with_magicstudio(prompt)
        if image:
            img_str = self._encode_image(image)
            if img_str:
                return {"success": True, "service": "MagicStudio", "image": img_str}

        return {
            "success": False,
            "error": "Failed to generate image with both services",
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
            logger.exception(f"Unexpected error in chat method: {str(e)}")
            return {"Error": str(e)}, 500
