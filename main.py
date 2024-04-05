from threading import Thread

import requests
import customtkinter as ctk

from utils.docker_utils import launch_container
from utils.host_utils import get_os_and_arch
from config import AgentDockerConfig


class ChatbotUI(ctk.CTk):

    def __init__(self, host_port_price_fetching_agent: int):
        super().__init__()

        self.host_port_price_fetching_agent = host_port_price_fetching_agent

        self.title("MORagents")
        self.geometry("400x500")

        self.chat_display = ctk.CTkTextbox(self, width=380, height=400, wrap="word")
        self.chat_display.pack(pady=20)

        self.user_input = ctk.CTkEntry(self, width=320, placeholder_text="Type your message here...")
        self.user_input.pack(side="left", padx=10)

        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message)
        self.send_button.pack(side="right")

    def send_message(self):
        user_message = self.user_input.get()
        self.display_message(f"You: {user_message}")

        self.user_input.delete(0, "end")
        Thread(target=self.call_rest_api, args=(user_message,)).start()

    def display_message(self, message):
        self.chat_display.insert("end", message + "\n\n")
        self.chat_display.see("end")

    def call_rest_api(self, message):
        try:
            url = f'http://localhost:{host_port_price_fetching_agent}/'
            data = {'prompt': message}
            response = requests.post(url, json=data, timeout=1000)

            if response.status_code == 200:
                bot_response = response.json()['response']
                self.chat_display.insert("end", f"Fetcher: {bot_response}\n\n")
            else:
                self.display_message("Fetcher: Sorry, there was a problem with the request.")
        except Exception as e:
            self.display_message(f"Fetcher: Failed to connect to the server. Error: {e}")

        self.chat_display.see("end")


if __name__ == "__main__":
    os_name, arch = get_os_and_arch()

    host_port_price_fetching_agent = launch_container(
        AgentDockerConfig.PRICE_FETCHER_IMAGE_NAME,
        AgentDockerConfig.PRICE_FETCHER_INTERNAL_PORT,
        AgentDockerConfig.PRICE_FETCHER_DOCKERFILE[arch]
    )

    app = ChatbotUI(host_port_price_fetching_agent=host_port_price_fetching_agent)
    app.mainloop()
