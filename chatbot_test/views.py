from django.shortcuts import render
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement
from chatterbot.response_selection import get_first_response
from better_profanity import profanity

# Define Fallback Responses
FallbackResponses = [
    "I didn't quite catch that. Can you rephrase?",
    "I'm still learning. Could you ask me something else?",
    "Sorry, I'm not sure I understand. Can you provide more context?"
]

# Initialize chatbot
chatbot = ChatBot('MyChatBot',
                  logic_adapters=[
                      {'import_path': 'chatterbot.logic.BestMatch',
                       'response_selection_method': get_first_response}
                  ],
                  preprocessors=[
                      'chatterbot.preprocessors.clean_whitespace'
                  ])

# Define the ProfanityFilterPreprocessor class
class ProfanityFilterPreprocessor:
    def __call__(self, statement):
        if profanity.contains_profanity(statement.text):
            statement.text = "I'm sorry, that isn't allowed in our domain."
        return statement

# Instantiate the ProfanityFilterPreprocessor
profanity_filter = ProfanityFilterPreprocessor()

# Add the preprocessor to the chatbot manually
chatbot.preprocessors.append(profanity_filter)

# Create a list trainer for interactive training
list_trainer = ListTrainer(chatbot)

# Train the chatbot with initial data
list_trainer.train([
    'Hi',
    'How are you doing?',
    'Hello',
    'What\'s up?',
    'Sorry',
    'No worries.',
    'Goodbye',
    'See you later!'
])

# Define the chat function for handling requests
"""
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Apply the profanity filter before getting the response
        filtered_input = profanity_filter(Statement(user_message))
        if profanity.contains_profanity(filtered_input.text):
            response = "I'm sorry, that isn't allowed in our domain."
        else:
            try:
                response = str(chatbot.get_response(filtered_input.text))
            except Exception as e:
                response = "An error occurred: " + str(e)
        
        return JsonResponse({'response': response})
    else:
        return render(request, 'chatbot_test/chat.html')"""

def chat_loop():
    with open('conversation_log.txt', 'a') as log_file:
        while True:
            user_input = input('You: ')

            # Check for exit conditions
            if user_input.lower() in ('q', 'exit', 'quit'):
                print('Bot: Exiting the chat.')
                break

            # Log the user's input
            log_file.write('User: {}\n'.format(user_input))

            # Check for profanity in user input
            if profanity.contains_profanity(user_input):
                print("Bot: Sorry, this isn't allowed in this domain.")
                log_file.write('Bot: Profanity detected and blocked.\n')
                continue  # Skip processing further if profanity detected

            # Get the bot's response
            bot_response = chatbot.get_response(user_input)

            # Check if the response is a fallback response
            if bot_response.text in FallbackResponses:
                print(bot_response.text)  # Print the fallback response
            else:
                # Log the bot's response
                log_file.write('Bot: {}\n'.format(bot_response))

                print('Bot:', bot_response)


# Define the interactive_train function for interactive training
def interactive_train():
    print('Start interactive training (type "exit" to quit):')
    exit_conditions = (":q", "quit", "exit")
    while True:
        user_input = input('You: ')
        if user_input.lower() in exit_conditions:
            break
        
        # Apply the profanity filter before getting the response
        filtered_input = profanity_filter(Statement(user_input))
        
        if profanity.contains_profanity(filtered_input.text):
            bot_response = "Bot: Sorry, this isn't allowed in this domain."
        else:
            bot_response = chatbot.get_response(filtered_input.text)
        
        print(bot_response)
        feedback = input('Was the response correct? (yes/no): ')
        
        if feedback.lower() == 'no':
            print('Please provide the correct response:')
            correct_response = input('You: ')
            
            # Train the chatbot with the correct response
            list_trainer.train([filtered_input.text, correct_response])
            print('Training completed for this pair.')
            print('Updated correct response:', correct_response)

# Run interactive training if the script is executed directly
if __name__ == '__main__':
    interactive_train()
# chat_loop()


