import customtkinter as ctk
import requests
from threading import Thread


class ChatbotUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chatbot")
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
            response = requests.post(
                url="http://localhost:5555/process_nlq",
                headers={"Content-Type": "application/json"},
                json={"NLQ": message}
            )
            if response.status_code == 200:
                bot_response = response.json().get("result", "Sorry, I couldn't process that.")
                self.chat_display.insert("end", f"Bot: {bot_response}\n\n")
            else:
                self.display_message("Bot: Sorry, there was a problem with the request.")
        except Exception as e:
            self.display_message(f"Bot: Failed to connect to the server. Error: {e}")

        self.chat_display.see("end")


if __name__ == "__main__":
    app = ChatbotUI()
    app.mainloop()
