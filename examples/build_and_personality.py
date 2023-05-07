from pyaipersonality import AIPersonality


if __name__=="__main__":
    personality = AIPersonality()
    personality.author = "ParisNeo"
    personality.version = "1.0.0"
    personality.name = "MyPersonality"
    personality.user_name = "my_username"
    personality.language = "en_US"
    personality.category = "Personalized"
    personality.personality_description = "This personality is a friendly and knowledgeable AI ready to assist you."
    personality.personality_conditioning = "MyPersonality is an AI designed to provide personalized help and have engaging conversations with users."
    personality.welcome_message = "Welcome! I am MyPersonality, your helpful AI assistant. How can I assist you today?"
    personality.user_message_prefix = "User:"
    personality.link_text = "\n"
    personality.ai_message_prefix = "MyPersonality:"
    personality.anti_prompts = ["#", "User:", "MyPersonality:"]
    personality.dependencies = ["dependency1", "dependency2", "dependency3"]
    personality.disclaimer = "This AI is not responsible for any actions taken based on its responses."
    personality.model_temperature = 0.7
    personality.model_n_predicts = 512
    personality.model_top_k = 30
    personality.model_top_p = 0.9
    personality.model_repeat_penalty = 1.2
    personality.model_repeat_last_n = 30
    personality.save_personality("personalities_zoo/english/tmp/test")
    print("Done")
    print(f"{personality}")