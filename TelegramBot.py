from typing import Final
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os

load_dotenv('.env')

TOKEN : Final = os.getenv("TOKEN")
USERNAME : Final = os.getenv("USERNAME")

print(USERNAME)
#================ Function for Commands ================
#update, which is an object that contains all the information and data that are coming from Telegram (like the message, the user who issued the command, etc)
#context, which is another object that contains information and data about the status of the library (like the Bot, the Application, the job_queue, etc)
async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = 0
    buttons = [[InlineKeyboardButton("BMI Calculator", callback_data="bmi")], [InlineKeyboardButton("Coming Soon", callback_data="soon")]]
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = "Hello, I'm a bot, Taily! Please choose one of the below operations to start for real.",
        reply_markup = InlineKeyboardMarkup(buttons)
        )
    
async def handle_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = 0
    print("Calculator Mode : OFF")
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = "Everything is reset"
        )
    await handle_help_command(update, context)
    
async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instruction = '''
Hey there! I'm Taily, your friendly BMI calculator.
Instead of being formal, Let me get to the point for ya..

"/start" - To allow you choose one of the operations you want
"/help" - To help you in understanding Taily Bot 
"/reset" - To reset the bot
"/bmi" - To start the operation of BMI calculator directly
    '''
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = instruction
        )

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = "I beg pardon, I do not understand this command."
        )

async def handle_bmi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Calculator Mode : ON")
    context.user_data["mode"] = 1
    context.user_data["weight"] = None
    context.user_data["height"] = None
    await handle_change_command(update, context)

async def handle_change_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = None
    context.user_data["height"] = None
    context.user_data["mode"] = 1
    print("Removed All Values")
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = "Just set things up for ya!\nEnter your Weight in pounds (lb)"
        )

async def handle_result_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton("One more try", callback_data="change")], [InlineKeyboardButton("Reset the Bot", callback_data="reset")]]
    result = perform_bmi_calculation(context.user_data['weight'], context.user_data['height'])
    msg = interpret_bmi(result)
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = msg,
        reply_markup= InlineKeyboardMarkup(buttons)
        )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query;
    #Indicate that callback query has been accepted
    await query.answer()
    #If bmi, trigger handle bmi command method
    if query.data == 'bmi':
        await handle_bmi_command(update, context)
    elif query.data == 'result':
        await handle_result_command(update, context)
    elif query.data == 'change':
        await handle_change_command(update, context)
    elif query.data == 'reset':
        await handle_reset_command(update, context)
    else:
        await context.bot.send_message(
            chat_id = update.effective_chat.id, 
            text = "Not Available"
        )
        await handle_help_command(update, context)

#============= Bot main feature ======================
def perform_bmi_calculation(weight : float, height : float) -> float:
    return round((weight * 703) / (height ** 2), 2)

def interpret_bmi(result : float) -> str:
    msg = None
    if result < 18.5:
        msg = f"Your BMI is {result}. According to the internet, that means you're... maybe a superhero in disguise!  (But seriously, consider talking to a healthcare professional about healthy weight gain.)"
    elif result < 25:
        msg = f"Your BMI is {result}. That's like... Goldilocks status! Just right! "
    elif result < 30:
        msg = f"Your BMI is {result}. You're like a cuddly bear!  Maybe time to consider a walk in the park for some fresh air and exercise. ‍♀️"
    else:
        msg = f"Your BMI is {result}. According to the internet, that means you're... still awesome! But remember, a healthy lifestyle is key!  Remember, this is just a lighthearted interpretation, it's always best to consult a healthcare professional."
    return msg
#============== Function for Messages ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    mode = context.user_data.get("mode", 0)
    msg = None
    buttons = [
        [InlineKeyboardButton("Get My BMI Result", callback_data = "result")],
        [InlineKeyboardButton("Need to change values", callback_data = "change")]
    ]

    print(context.user_data)        

    if mode and not context.user_data["weight"] is None and not context.user_data["height"] is None:
        print("Ready For Result", context.user_data)
        #Asking the user if he wants to change the values or get the result
        msg = f"Weight: {context.user_data["weight"]} pounds (lb)\nHeight: {context.user_data["height"]} inches (in)"
        await update.message.reply_text(text = msg, reply_markup = InlineKeyboardMarkup(buttons))
        return
    
    elif mode:
        print("Need something", context.user_data)
        msg = "Mode is ON"
        
        try:
            #Converting the string number into float
            input = abs(float(update.message.text))
            #Checking whether those input values are zeros
            if(input == 0):
                raise ValueError("A human can't have 0 values for their weight or height...")
            if context.user_data["weight"] is None:
                context.user_data["weight"] = input
                msg = f"Weight: {context.user_data["weight"]} lbs\nEnter your height in inches(in)"

            elif context.user_data["height"] is None:
                context.user_data["height"] = input                
                msg = f"Weight: {context.user_data["weight"]} pounds (lb)\nHeight: {context.user_data["height"]} inches (in)"
                await update.message.reply_text(text = msg, reply_markup = InlineKeyboardMarkup(buttons))
                return
            
        except ValueError as err:
            print(err)
            msg = "Can't add zeros... Go again!"

        except Exception as err:
            print(err)
            msg = "Invalid input, Enter only numbers (For Example: 59.5), Go again!"
        

    else:
        print("Not in the Calculator Mode")
        msg = f"You haven't chosen an operation yet.\nSo, All i can do is echo your message back XD\n{update.message.text}"
    
    await update.message.reply_text(msg)

#=============== Function for handling errors ================
async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"ERROR => {context.error}")
    await context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = "Sorry, mate... An unexpected error occured...\nMay be, try again"
        )

if __name__ == '__main__':
    print("Running the bot...")
    #Create an application object
    application = ApplicationBuilder().token(TOKEN).build()
    #To listen to /start command and register an action
    application.add_handler(CommandHandler('start', handle_start_command))
    #The listen to /help command and register an action
    application.add_handler(CommandHandler('help', handle_help_command))
    #To reset the whole thing
    application.add_handler(CommandHandler('reset', handle_reset_command))
    #To turn on the mode of BMI calculator
    application.add_handler(CommandHandler('bmi', handle_bmi_command))
    #To echo all text messages
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    #To Handle Button response
    application.add_handler(CallbackQueryHandler(handle_query))
    #To respond to unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
    #To handle Errors
    application.add_error_handler(handle_error)
    #runs the bot until CTRL+C is hit
    application.run_polling()
