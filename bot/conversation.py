import re
from typing import Optional

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ParseMode, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, MessageHandler, Filters, \
    CallbackQueryHandler

# Conversation states
(
    BASE,
    CHECK_RIGHT_STEP_1,
    CHECK_RIGHT_STEP_2,
    WAITING_INSTA,
    WAITING_VK,
    WAITING_APPROVE,
    WAITING_PAYMENT,
    WAITING_FOR_MANUAL_CODE,
    READY_DASHBOARD,
    ADMIN_DASHBOARD,
    ADMIN_BROADCAST,
    ADMIN_CHECKIN,
) = range(1, 13)


CALLBACK_BUTTON_START_AGAIN = "Начать заново"
CALLBACK_BUTTON_YES = "Да"
CALLBACK_BUTTON_CHECK_NEW_AGE = "Другой возраст"
CALLBACK_BUTTON_NO = "Нет"
CALLBACK_BUTTON_DONT_KNOW = "Не знаю"
BUTTON_CHECK_RIGHTS = "Проверить право"
BUTTON_START_AGAIN = "Начать заново"
BUTTON_BACK = "В начало"


def action_state_answer(update: Update, context: CallbackContext):
    action_to_base(update, context)
    return None


def action_to_base(update: Update, context: CallbackContext):

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Привет! Это бот IsraelWay!",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            [[str(BUTTON_CHECK_RIGHTS), str(BUTTON_BACK)]],
            one_time_keyboard=False,
            resize_keyboard=True,
        ),
    )

    context.bot.send_message(
        chat_id=update.effective_user.id,
        parse_mode=ParseMode.HTML,
        text=f"Держите нашу <a href='https://bit.ly/iway-deck'>презентацию</a> - "
        f"тут ответы на большинство вопросов, которые, возможно, у вас возникнут.\n\n"
        f"Если хотите узнать что-то более подробно, то пишите вот сюда @israelway_IW",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Обратиться к координатору', url='https://t.me/israelway_IW')]
        ])
    )

    return BASE


def action_to_check_rights_step_1(update: Update, context: CallbackContext):
    update.message.reply_html(
        f"Ответы на два вопроса помогут вам понять, "
        f"подходите ли вы для участия в финансируемых программах, "
        f"и предложат список программ, соответствующих вашим критериям.\n\n"
        f"Вопрос первый. Есть ли у вас еврейские корни? "
        f"(Ваши или вашего супруга или супруги бабушка или дедушка со стороны матери или со стороны отца - евреи)",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text=str(CALLBACK_BUTTON_YES), callback_data=f"{CALLBACK_BUTTON_YES}"),
                InlineKeyboardButton(text=str(CALLBACK_BUTTON_NO), callback_data=f"{CALLBACK_BUTTON_NO}")
            ],
            [InlineKeyboardButton(text=str(CALLBACK_BUTTON_DONT_KNOW), callback_data=f"{CALLBACK_BUTTON_DONT_KNOW}")],
        ]))

    return CHECK_RIGHT_STEP_1


def action_check_age(update: Update, context: CallbackContext):
    first_number_match = re.search(r'\d+', update.message.text)

    if not first_number_match:
        update.message.reply_html(
            f"Напишите в ответ число, пожалуйста"
        )
        return None

    first_number = int(first_number_match.group(0))
    update.message.reply_html(
        f"Вы указали возраст: {first_number}",
    )

    if first_number < 17 or first_number > 40:
        update.message.reply_html(
            f"К сожалению, вы не можете претендовать на участие в программах Маса и Онвард, "
            f"однако вы можете проверить варианты сотрудничества с нами и переход к переписке с координатором",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
                [InlineKeyboardButton(text='Обратиться к координатору', url='https://t.me/israelway_IW')]
            ])
        )

    if first_number in range(17, 31):
        update.message.reply_html(
            f"Поздравляем, вы можете подавать вашу кандидатуру на участие в программах <a href='https://israelway.ru/masa/all-programs/'>МАСА</a> длительностью до шести месяцев, "
            f"на программу <a href='https://israelway.ru/onward-campus'>Онвард Кампус</a> длительностью до месяца "
            f"и на программу <a href='https://israelway.ru/onward-volunteering'>Онвард волонтёр</a> длительностью до двух недель.",

            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='МАСА 6 месяцев', url='https://israelway.ru/masa/all-programs/')],
                [InlineKeyboardButton(text='Онвард Кампус', url='https://israelway.ru/onward-campus')],
                [InlineKeyboardButton(text='Онвард волонтёр', url='https://israelway.ru/onward-volunteering')],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
            ])
        )

    if first_number in range(31, 35):
        update.message.reply_html(
            f"Поздравляем, вы можете подавать вашу кандидатуру на участие в программах <a href='https://israelway.ru/masa/all-programs/'>МАСА</a> длительностью до шести месяцев "
            f"и на программу <a href='https://israelway.ru/onward-volunteering'>Онвард волонтёр</a> длительностью до двух недель.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='МАСА 6 месяцев', url='https://israelway.ru/masa/all-programs/')],
                [InlineKeyboardButton(text='Онвард волонтёр', url='https://israelway.ru/onward-volunteering')],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
            ])
        )

    if first_number in range(35, 41):
        update.message.reply_html(
            f"Поздравляем, вы можете подавать вашу кандидатуру на участие в "
            f"программе <a href='https://israelway.ru/onward-volunteering'>Онвард волонтёр</a> длительностью до двух недель",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Онвард волонтёр', url='https://israelway.ru/onward-volunteering')],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
            ])
        )

    return None


def callback_action_check_age_again(update: Update, context: CallbackContext) -> Optional[int]:
    answer = update.callback_query.data

    update.callback_query.answer()
    update.callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))

    if answer == CALLBACK_BUTTON_CHECK_NEW_AGE:
        context.bot.send_message(
            update.effective_user.id,
            "Сколько вам лет? (число от 17 до 40 включительно)",
            parse_mode=ParseMode.HTML,
        )
        return CHECK_RIGHT_STEP_2

    return None


def action_step_1_answer(update: Update, context: CallbackContext) -> Optional[int]:
    answer = update.callback_query.data

    update.callback_query.answer()
    update.callback_query.delete_message()

    if answer == CALLBACK_BUTTON_YES:
        context.bot.send_message(
            update.effective_user.id,
            "Сколько вам лет? (число от 17 до 40 включительно)",
            parse_mode=ParseMode.HTML,
        )
        return CHECK_RIGHT_STEP_2

    if answer == CALLBACK_BUTTON_NO:
        context.bot.send_message(
            update.effective_user.id,
            "К сожалению, вы не сможете получить финансирование, "
            "но можете принять участие в программах за полную стоимость.\n"
            "Перейти к списку программ - переход сюда: <a href='https://israelway.ru/'>https://israelway.ru/</a>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN), callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ]),
            parse_mode=ParseMode.HTML,
        )
        return None

    if answer == CALLBACK_BUTTON_DONT_KNOW:
        context.bot.send_message(
            update.effective_user.id,
            "Проверьте свою родословную и убедитесь, что вы подпадаете под закон “О возвращении” "
            "(ссылка: <a href='https://www.gov.il/ru/Departments/Policies/government_law_of_return_nativ'>https://www.gov.il/ru/Departments/Policies/government_law_of_return_nativ</a>)"
            " и, если результат положительный, вернитесь к процессу регистрации",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN), callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ]),
            parse_mode=ParseMode.HTML,
        )
        return None

    return None



conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", action_to_base),
        MessageHandler(Filters.text, action_to_base),
    ],
    states={
        BASE: [
            MessageHandler(
                Filters.regex(f"^{str(BUTTON_CHECK_RIGHTS)}"), action_to_check_rights_step_1
            )
        ],
        CHECK_RIGHT_STEP_1: [
            MessageHandler(Filters.regex(f"^{BUTTON_CHECK_RIGHTS}$"), action_to_check_rights_step_1),
            CallbackQueryHandler(action_step_1_answer,
                                 pattern=rf"{CALLBACK_BUTTON_YES}|{CALLBACK_BUTTON_NO}|{CALLBACK_BUTTON_DONT_KNOW}"),
        ],
        CHECK_RIGHT_STEP_2: [
            MessageHandler(Filters.regex(f"^{BUTTON_CHECK_RIGHTS}$"), action_to_check_rights_step_1),
            MessageHandler(Filters.regex(f"^{BUTTON_BACK}$"), action_to_base),
            MessageHandler(Filters.text, action_check_age),
            CallbackQueryHandler(callback_action_check_age_again,
                                 pattern=rf"{CALLBACK_BUTTON_CHECK_NEW_AGE}"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(action_to_base, pattern=rf"{CALLBACK_BUTTON_START_AGAIN}"),
        MessageHandler(Filters.regex(f"^{BUTTON_CHECK_RIGHTS}$"), action_to_check_rights_step_1),
        MessageHandler(Filters.text, action_state_answer),
    ],
    name="IsraelWay_Conv",
    # persistent=True,
    per_chat=False,
    per_message=False,
)
