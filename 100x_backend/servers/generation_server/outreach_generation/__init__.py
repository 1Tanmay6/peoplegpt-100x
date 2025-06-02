def generate_failed_message(name: str) -> str:
    return (
        f"Dear {name},\n\n"
        "Thank you for applying to our company. After careful review, we regret to inform you that "
        "your application did not pass our initial screening stage. We appreciate the time and effort "
        "you put into your submission and encourage you to apply again in the future.\n\n"
        "Best regards,\nHR Team"
    )


def generate_passed_message(name: str) -> str:
    return (
        f"Hi {name},\n\n"
        "Thank you for applying. We're pleased to let you know that your application has moved past our "
        "initial screening. We'll be in touch shortly with more details about the next steps and interviews.\n\n"
        "Stay tuned!\nHR Team"
    )


__all__ = ["generate_failed_message", "generate_passed_message"]
