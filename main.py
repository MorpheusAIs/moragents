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
        self.geometry("420x500")
        self.resizable(False, True)

        self.chat_display = ctk.CTkTextbox(self, width=400, height=400, wrap="word")
        self.chat_display.pack(pady=20)

        self.user_input = ctk.CTkEntry(self, width=320, placeholder_text="Ask about price, market cap, or TVL")
        self.user_input.pack(side="left", padx=10)
        self.user_input.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message, width=100, height=30)
        self.send_button.pack(side="right", padx=10)
        self.send_button.bind("<Return>", lambda event: self.send_message())
        self.send_button.focus_set()

        # Warm-up step: Silently fetch BTC price and give user notice
        self.display_message("Waking up agent \"Fetcher\"...\n"
                             "Just a few seconds...\n\n")
        self.after(2000, self.warm_up_agent)

    def warm_up_agent(self):
        try:
            url = f'http://localhost:{self.host_port_price_fetching_agent}/'
            data = {'prompt': 'BTC price'}
            response = requests.post(url, json=data, timeout=1000)

            if response.status_code == 200:
                self.display_message("Fetcher agent is ready!\nYou can ask about prices, market caps, and TVLs\n\n\n")
            else:
                self.display_message("Fetcher agent warm-up failed.")
        except Exception as e:
            self.display_message(f"Fetcher: Failed to connect to the agent during warm-up. Error: {e}")

    def send_message(self):
        user_message = self.user_input.get()
        self.display_message(f"You: {user_message}")

        self.user_input.delete(0, "end")
        self.display_message("Fetcher: Working...")
        Thread(target=self.call_rest_api, args=(user_message,)).start()

    def display_message(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def call_rest_api(self, message):
        try:
            url = f'http://localhost:{self.host_port_price_fetching_agent}/'
            data = {'prompt': message}
            response = requests.post(url, json=data, timeout=1000)

            self.chat_display.configure(state="normal")
            thinking_index = self.chat_display.search("Fetcher: Working...", "end", backwards=True)
            if thinking_index:
                self.chat_display.delete(thinking_index, f"{thinking_index}+1l")
            else:
                self.chat_display.insert("end", "\n")
            if response.status_code == 200:
                bot_response = response.json()['response']
                self.chat_display.insert("end", f"Fetcher: {bot_response}\n")
            else:
                self.chat_display.insert("end", "Fetcher: Sorry, there was a problem with the request.\n")
            self.chat_display.configure(state="disabled")
        except Exception as e:
            self.chat_display.configure(state="normal")
            thinking_index = self.chat_display.search("Fetcher: Working...", "end", backwards=True)
            if thinking_index:
                self.chat_display.delete(thinking_index, f"{thinking_index}+1l")
            else:
                self.chat_display.insert("end", "\n")
            self.chat_display.insert("end", f"Fetcher: Failed to connect to the server. Error: {e}\n")
            self.chat_display.configure(state="disabled")

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
