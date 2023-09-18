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

START_ROUTES, CHOICES, FILES, QUESTIONS, END_ROUTES = range(5)

ONE, TWO = range(2)

def Ostad(college, ostad):
    if college == "bargh": # .....name
        if ostad=='vahdat':
            text= '"استاد وثوقی وحدت"'
        elif ostad=='hashemi':
            text= '"استاد هاشمی"'
    
    return text

start_keyboard = [ # college's name
    [
        InlineKeyboardButton("فیزیک", callback_data= "fizik"),
        InlineKeyboardButton("ریاضی", callback_data= "riazi"),
    ],
    [
        InlineKeyboardButton("شیمی", callback_data= "shimi"),
        InlineKeyboardButton("برق", callback_data= "bargh")
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
            InlineKeyboardButton("دیدن نتایج", callback_data= 'k' + query.data),
            InlineKeyboardButton("ثبت نظر", callback_data= 'n' + query.data),
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


    converted_1 = {}
    converted_2 = {}
    converted_3 = {}
    q_a = 0
    q_b = 0
    q_c = 0
    number = 0
    with open('names.json', mode='r') as my_file:
        try:
            converted_1 = json.loads(my_file.read())
            converted_2 = converted_1[college]
            converted_3 = converted_2[ostad]
            q_a = converted_3["A"]
            q_b = converted_3["B"]
            q_c = converted_3["C"]
            number = converted_3["n"]# voters number
            
            if  number == 0:
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "تاکنون دیدگاهی برای این استاد ثبت نشده.")
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "یه استاد دیگه؟", reply_markup=reply_markup)
            else:
                A = round((q_a*100)/(number*5))
                B = round((q_b*100)/(number*5))
                C = round((q_c*100)/(number*5))

                a = round(A/10)
                b = round(B/10)
                c = round(C/10)
                # برای معیارهای خوب و بد🟦🟥🟩🔵🔴🟢⚫⬛🌕🌑⭐
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "کیفیت تدریس:\n" + str(A) + "% " + a*"🌕" + "\nنمره دهی:\n" + str(B) + "% " + b*"🌕" + "\nاخلاق:\n" + str(C) + "% " + c*"🌕")
                await context.bot.send_message(chat_id=update.effective_chat.id, text= "می خوای ادامه بدی؟", reply_markup=reply_markup)
        
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text= "تاکنون دیدگاهی برای این استاد ثبت نشده.")
            await context.bot.send_message(chat_id=update.effective_chat.id, text= "یه استاد دیگه؟", reply_markup=reply_markup)
   
    return END_ROUTES


async def rate_A(update: Update, context: ContextTypes.DEFAULT_TYPE):# first question
    
    subject = '«کیفیت تدریس»' #//////
    query = update.callback_query
    await query.answer()
    f = query.data.find('?')
    college = query.data[1:f]
    ostad = query.data[f+1:]

    tx = Ostad(college, ostad)
    await query.edit_message_text(text= tx)

    pre_messages_keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data= 'B' + query.data[1:] + '1'),
            InlineKeyboardButton("2️⃣", callback_data= 'B' + query.data[1:] + '2'),
            InlineKeyboardButton("3️⃣", callback_data= 'B' + query.data[1:] + '3'),
            InlineKeyboardButton("4️⃣", callback_data= 'B' + query.data[1:] + '4'),
            InlineKeyboardButton("5️⃣", callback_data= 'B' + query.data[1:] + '5')
        ],
        # [
        #     InlineKeyboardButton("بدون جواب", callback_data= 'B' + query.data[1:] + '0')
        # ]

    ]
    reply_markup = InlineKeyboardMarkup(pre_messages_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'از یک تا پنج نمره دهید: ' + subject , reply_markup=reply_markup)
    return QUESTIONS


async def rate_B(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    subject = '«نمره دهی»' #//////
    query = update.callback_query
    await query.answer()
    pre_messages_keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data= 'C' + query.data[1:] + '1'),
            InlineKeyboardButton("2️⃣", callback_data= 'C' + query.data[1:] + '2'),
            InlineKeyboardButton("3️⃣", callback_data= 'C' + query.data[1:] + '3'),
            InlineKeyboardButton("4️⃣", callback_data= 'C' + query.data[1:] + '4'),
            InlineKeyboardButton("5️⃣", callback_data= 'C' + query.data[1:] + '5')
        ],
        # [
        #     InlineKeyboardButton("بدون جواب", callback_data= 'C' + query.data[1:] + '0')
        # ]

    ]
    reply_markup = InlineKeyboardMarkup(pre_messages_keyboard)
    await query.edit_message_text(text= 'از یک تا پنج نمره دهید: ' + subject , reply_markup=reply_markup)
    return QUESTIONS


async def rate_C(update: Update, context: ContextTypes.DEFAULT_TYPE):# last question
    
    subject = '«اخلاق»' #//////
    query = update.callback_query
    await query.answer()
    pre_messages_keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data= 'L' + query.data[1:] + '1'),
            InlineKeyboardButton("2️⃣", callback_data= 'L' + query.data[1:] + '2'),
            InlineKeyboardButton("3️⃣", callback_data= 'L' + query.data[1:] + '3'),
            InlineKeyboardButton("4️⃣", callback_data= 'L' + query.data[1:] + '4'),
            InlineKeyboardButton("5️⃣", callback_data= 'L' + query.data[1:] + '5')
        ],
        # [
        #     InlineKeyboardButton("ذخیره", callback_data= 'L' + query.data[1:] + '0')# ثبت یا ذخیره
        # ]

    ]
    reply_markup = InlineKeyboardMarkup(pre_messages_keyboard)
    await query.edit_message_text(text= 'از یک تا پنج نمره دهید: ' + subject , reply_markup=reply_markup)
    return QUESTIONS


async def save_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    f = query.data.find('?')
    college = query.data[1:f]
    ostad = query.data[f+1:-3]# -questions number
    
    q_A = int(query.data[-3])
    q_B = int(query.data[-2])
    q_C = int(query.data[-1])

    converted_1 = {}
    converted_2 = {}
    converted_3 = {}
    q_a = 0
    q_b = 0
    q_c = 0
    number = 0
    with open('names.json', mode='r') as my_file:
        try:
            converted_1 = json.loads(my_file.read())
            converted_2 = converted_1[college]
            converted_3 = converted_2[ostad]
            q_a = converted_3["A"]
            q_b = converted_3["B"]
            q_c = converted_3["C"]
            number = converted_3["n"]# voters number
        except:
            pass
        q_a += q_A
        q_b += q_B
        q_c += q_C
        number += 1

        converted_3["A"] = q_a
        converted_3["B"] = q_b
        converted_3["C"] = q_c
        converted_3["n"] = number

        converted_2[ostad] = converted_3
        converted_1[college] = converted_2
    with open('names.json', mode='w') as my_file:
        my_file.write(json.dumps(converted_1, indent=4))

    await query.edit_message_text(text = 'با تشکر نظر شما ثبت شد.🤝')
    reply_markup = InlineKeyboardMarkup(end_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text= 'می خوای ادامه بدی؟', reply_markup=reply_markup)    
    return END_ROUTES


# //////////
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
                CallbackQueryHandler(fizik, pattern="^" + "fizik" + "$"),
                CallbackQueryHandler(riazi, pattern="^" + "riazi" + "$"),
                CallbackQueryHandler(shimi, pattern="^" + "shimi" + "$"),
                CallbackQueryHandler(bargh, pattern="^" + "bargh" + "$"),
            ],
            CHOICES: [CallbackQueryHandler(choice)],
            FILES: [
                CallbackQueryHandler(read, pattern= 'k'),
                CallbackQueryHandler(rate_A, pattern= 'n') # کیفیت تدریس
            ],
            QUESTIONS: [
                CallbackQueryHandler(rate_B, pattern= 'B'), # نمره دهی
                CallbackQueryHandler(rate_C, pattern= 'C'), # اخلاق
                CallbackQueryHandler(save_rate, pattern= 'L'),
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