from chatbot.company_bot import CompanyBot


class ProtectedAssistant:
    def __init__(self, mode: str = "PROTECTION"):
        self.mode = mode
        self.bot = CompanyBot(mode=mode)

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.bot.set_mode(mode)

    def respond(self, message: str, defender_decision: dict) -> dict:
        return self.bot.respond(message, defender_decision)
