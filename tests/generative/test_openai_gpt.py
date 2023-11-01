from app.generative.openai_gpt import parse_options


def test_parse_options():
    response_content = """Option 1:
"Je vais à Amsterdam."
"I'm going to Amsterdam."

Option 2:
"Je n'ai pas encore décidé de la ville exacte."
"I haven't decided on the exact city yet."

Option 3:
"Ma destination est Rotterdam."
"My destination is Rotterdam."
"""

    options = parse_options(response_content)
    assert options == [
        (
            "Je vais à Amsterdam.",
            "I'm going to Amsterdam.",
        ),
        (
            "Je n'ai pas encore décidé de la ville exacte.",
            "I haven't decided on the exact city yet.",
        ),
        (
            "Ma destination est Rotterdam.",
            "My destination is Rotterdam.",
        ),
    ]
