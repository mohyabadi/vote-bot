import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
    ApplicationBuilder
)

START_ROUTES, CHOICES, FILES, END_ROUTES = range(4)
VAHDAT_W, HASHEMI_W = range(5,7) # .....name

ONE, TWO, THREE = range(3)
Fizik, Riazi, Shimi, Bargh = range(4) # college's name

def Ostad(college, ostad):
    if college == str(Bargh): # .....name
        if ostad=='vahdat':
            text= 'استاد وثوقی وحدت'
        elif ostad=='hashemi':
            text= 'استاد هاشمی'
    
    return text

start_keyboard = [ # college's name
    [
        InlineKeyboardButton("فیزیک", callback_data=str(Fizik)),
        InlineKeyboardButton("ریاضی", callback_data=str(Riazi)),
    ],
    [
        InlineKeyboardButton("شیمی", callback_data=str(Shimi)),
        InlineKeyboardButton("برق", callback_data=str(Bargh))
    ]
]

end_keyboard = [
    [
        InlineKeyboardButton("آره", callback_data=str(ONE)),
        InlineKeyboardButton("نه دیگه", callback_data=str(TWO)),
    ]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    reply_markup = InlineKeyboardMarkup(start_keyboard)
    await update.message.reply_text("سلام. دانشکده رو انتخاب کن.", reply_markup=reply_markup)
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    reply_markup = InlineKeyboardMarkup(start_keyboard)
    await query.edit_message_text("دانشکده رو انتخاب کن.", reply_markup=reply_markup)
    return START_ROUTES


# college's functions
async def bargh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    bargh_keyboard = [ # .....name
        [
            InlineKeyboardButton("دکتر وثوقی وحدت", callback_data= query.data + '?' + 'vahdat'),
            InlineKeyboardButton("دکتر هاشمی", callback_data= query.data + '?' + 'hashemi')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(bargh_keyboard)
    await query.edit_message_text(text="استادت رو انتخاب کن.", reply_markup=reply_markup)
    return CHOICES


async def fizik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def riazi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def shimi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass
#.....


async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice_keyboard = [
        [
        InlineKeyboardButton("خواندن نظرات", callback_data='k' + query.data),
        InlineKeyboardButton("نظر دادن", callback_data='n' + query.data)
        ]
    ]
    f = query.data.find('?')
    college = query.data[:f]
    ostad = query.data[f+1:]

    tx = Ostad(college, ostad)
    reply_markup = InlineKeyboardMarkup(choice_keyboard)
    await query.edit_message_text(text = tx, reply_markup=reply_markup)
    return FILES


async def read(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    f = query.data.find('?')
    college = query.data[1:f]
    ostad = query.data[f+1:]

    tx = Ostad(college, ostad)
    await query.edit_message_text(text = tx)
    reply_markup = InlineKeyboardMarkup(end_keyboard)

    converted = {}
    with open('names.json', mode='r') as my_file2:
        try:
            converted = json.loads(my_file2.read())
            r_nazar = converted[ostad]
            if  r_nazar == "":
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "تاکنون دیدگاهی برای این استاد ثبت نشده.")
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "یه استاد دیگه؟", reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text= r_nazar)
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "می خوای ادامه بدی؟", reply_markup=reply_markup)
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text= "تاکنون دیدگاهی برای این استاد ثبت نشده.")
            await context.bot.send_message(chat_id=update.effective_chat.id, text= "یه استاد دیگه؟", reply_markup=reply_markup)
    return END_ROUTES


async def b_write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    f = query.data.find('?')
    college = query.data[1:f]
    ostad = query.data[f+1:]

    tx = Ostad(college, ostad)
    await query.edit_message_text(text= tx)

    pre_messages_keyboard = [ # prepared messages
        [InlineKeyboardButton("خوب درس میدهند.", callback_data= ostad + str(ONE))],
        [InlineKeyboardButton("خوب درس نمی دهند.", callback_data= ostad + str(TWO))],
        [InlineKeyboardButton("حتما پیشنهادشون می کنم.", callback_data= ostad + str(THREE))],
    ]
    reply_markup = InlineKeyboardMarkup(pre_messages_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'نظرت رو در قالب یک پیام ارسال کن یا این پیام های زیر استفاده کن.', reply_markup=reply_markup)
    
    if college==str(Bargh): # .....name
        if ostad=='vahdat':
            return VAHDAT_W
        elif ostad=='hashemi':
            return HASHEMI_W


async def pre_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    ostad = query.data[:-1]
    msg = query.data[-1:]

    if msg==str(ONE): # prepared messages
        new_data = "خوب درس میدهند."
    elif msg==str(TWO):
        new_data = "خوب درس نمی دهند."
    elif msg==str(THREE):
        new_data = "حتما پیشنهادشون می کنم."

    converted = {}
    previous_data = ""
    with open('names.json', mode='r') as my_file:
        try:
            converted = json.loads(my_file.read())
            previous_data = "\n\n" + converted[ostad]
        except:
            pass
    with open('names.json', mode='w') as my_file:
        converted[ostad] = "🔵 "+ new_data + previous_data
        my_file.write(json.dumps(converted, indent=4))
    
    await query.edit_message_text(text = new_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'با تشکر نظر شما ثبت شد.🤝')
    reply_markup = InlineKeyboardMarkup(end_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'می خوای ادامه بدی؟', reply_markup=reply_markup)
    return END_ROUTES


# professor's functions
async def vahdat_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ostad = "vahdat" # .....name
    user = update.message.from_user
    logger.info("message of %s about dr.%s : %s", user.first_name, ostad, update.message.text)

    converted = {}
    previous_data = ""
    with open('names.json', mode='r') as my_file:
        try:
            converted = json.loads(my_file.read())
            previous_data = "\n\n" + converted[ostad]
        except:
            pass
    with open('names.json', mode='w') as my_file:
        converted[ostad] = "🔵 "+ update.message.text + previous_data
        my_file.write(json.dumps(converted, indent=4))
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'با تشکر نظر شما ثبت شد.🤝')
    reply_markup = InlineKeyboardMarkup(end_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'می خوای ادامه بدی؟', reply_markup=reply_markup)
    return END_ROUTES


async def hashemi_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ostad = "hashemi" # .....name
    user = update.message.from_user
    logger.info("message of %s about dr.%s : %s", user.first_name, ostad, update.message.text)

    converted = {}
    previous_data = ""
    with open('names.json', mode='r') as my_file:
        try:
            converted = json.loads(my_file.read())
            previous_data = "\n\n" + converted[ostad]
        except:
            pass
    with open('names.json', mode='w') as my_file:
        converted[ostad] = "🔵 "+ update.message.text + previous_data
        my_file.write(json.dumps(converted, indent=4))

    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'با تشکر نظر شما ثبت شد.🤝')
    reply_markup = InlineKeyboardMarkup(end_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'می خوای ادامه بدی؟', reply_markup=reply_markup)
    return END_ROUTES
#.....


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="به امید دیدار\nبرای شروع دوباره /start رو بفرست.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text("به امید دیدار\nبرای شروع دوباره /start رو بفرست.")
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='من این دستور رو نمی فهمم :(')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= '''سلام. لطفا هنگام نظر دادن به این نکات دقت کنید:
🔴 عادلانه و با انصاف رای دهید.
🔴 هم به نقاط قوت و هم به نقاط ضعف اشاره کنید.
🔴 از به کاربردن کلمات زشت خودداری کنید. در صورتی که پیام شما حاوی عبارات توهین آمیز باشد، حذف خواهد شد.

🔴 برای استفاده بهتر از نظر شما در پیام خود به موارد زیر اشاره کنید:
👈نام درس یا درس هایی که با استاد داشتید (مثال: ریاضی2)،
👈سال و ترم ارائه (مثال: 401-402 ، نیمسال دوم یا ترم زوج)،
👈همچنین حدود نمره ای که گرفتید (مثال: 15)

🔴 همچنین در هنگام رای دادن معیارهای زیر را در نظر داشته باشید:
👈 کیفیت و روش تدریس
👈 اخلاق
👈 نمره دهی
👈 دانش استاد
👈 معیار ارزشیابی
👈 حجم کاری(امتحان، کوئیز، تمرین، گزارش و...)
👈 منبع و جزوه
و...''')


if __name__ == '__main__':
    application = ApplicationBuilder().token('6320447981:AAEmsFPnh0_JGaae9gj7PqVZJRH-3Gndr4g').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [ # college's functions
                CallbackQueryHandler(fizik, pattern="^" + str(Fizik) + "$"),
                CallbackQueryHandler(riazi, pattern="^" + str(Riazi) + "$"),
                CallbackQueryHandler(shimi, pattern="^" + str(Shimi) + "$"),
                CallbackQueryHandler(bargh, pattern="^" + str(Bargh) + "$"),
            ],
            CHOICES: [CallbackQueryHandler(choice)],
            FILES: [
                CallbackQueryHandler(read, pattern= 'k'),
                CallbackQueryHandler(b_write, pattern= 'n')
            ],
            VAHDAT_W: [ # professor's functions
                MessageHandler(filters.TEXT & ~filters.COMMAND, vahdat_write),
                CallbackQueryHandler(pre_message),
            ],
            HASHEMI_W: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, hashemi_write),
                CallbackQueryHandler(pre_message),
            ],

            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    help_handler = CommandHandler('help', help)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(conv_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)