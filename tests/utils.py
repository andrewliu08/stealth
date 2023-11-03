def messages_equal(message1, message2):
    return (
        message1.sender == message2.sender
        and message1.content == message2.content
        and message1.translation == message2.translation
        and message1.tts_uri == message2.tts_uri
        and message1.tts_task_id == message2.tts_task_id
    )


def conversations_equal(conversation1, conversation2):
    return (
        conversation1.id == conversation2.id
        and len(conversation1.history) == len(conversation2.history)
        and conversation1.intro_message == conversation2.intro_message
        and all(
            messages_equal(message1, message2)
            for message1, message2 in zip(conversation1.history, conversation2.history)
        )
        and conversation1.user_lang == conversation2.user_lang
        and conversation1.resp_lang == conversation2.resp_lang
    )
