RESPONSE_OPTIONS_PROMPT = '''You are a fluent {0} speaker having a conversation in {0}. The conversation so far is in triple quotes:
"""
{1}
"""
Provide {2} of the most plausible and helpful response options "Person 1" would say. The responses should be brief, cover different possibilities, and contain ONLY {0}. Put any unknown information in square brackets. Follow the format in the triple quotes:
"""
<Start>
"<Response 1 in {0}>"
<End>
<Start>
"<Response 2 in {0}>"
<End>
<Start>
"<Response 3 in {0}>"
<End>
"""
'''

RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS = '''You are a fluent {0} speaker having a conversation in {0}. The conversation so far is in triple quotes:
"""
{2}
"""
Provide {3} options for what you might say to the other person. For each option, provide an {1} translation of what you said. Follow the format in the triple quotes:
"""
Option 1:
"Response 1 in {0}"
"Translation of response 1 in {1}"

Option 2:
"Response 2 in {0}"
"Translation of response 2 in {1}"

Option 3:
"Response 3 in {0}"
"Translation of response 3 in {1}"
"""
'''

STARTER_PROMPT_WITH_TRANSLATIONS_AND_GOAL = '''You are a fluent {0} speaker. You are having a conversation in {0} with the goal: "{1}".
Provide {2} options for how you might start the conversation with the other person. For each option, provide an English translation of what you said. Follow the format in the triple quotes:
"""
Option 1:
"Response 1 in {0}"
"Translation of response 1 in English"

Option 2:
"Response 2 in {0}"
"Translation of response 2 in English"

Option 3:
"Response 3 in {0}"
"Translation of response 3 in English"
"""
'''

RESPONSE_OPTIONS_PROMPT_WITH_TRANSLATIONS_AND_GOAL = '''You are a fluent {0} speaker. You are having a conversation in {0} with the goal: "{1}". The conversation so far is in triple quotes:
"""
{2}
"""
Provide {3} options for what you might say to the other person. For each option, provide an English translation of what you said. Follow the format in the triple quotes:
"""
Option 1:
"Response 1 in {0}"
"Translation of response 1 in English"

Option 2:
"Response 2 in {0}"
"Translation of response 2 in English"

Option 3:
"Response 3 in {0}"
"Translation of response 3 in English"
"""
'''
