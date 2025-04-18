import re
from typing import Optional

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, MessageHandler, \
    CallbackQueryHandler, filters, BaseHandler
from bot.error_handler import error_handler
from bot.texts import *
from bot.texts import LINK_DOWNLOAD_APP, BUTTON_DOWNLOAD_APP

# Conversation states
(
    CHECK_RIGHT_STEP_1,
    CHECK_RIGHT_STEP_2,
) = range(1, 3)


async def action_welcome(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"👋",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            [
                [str(BUTTON_CHECK_RIGHTS)],
                [str(BUTTON_GET_GIFT), str(BUTTON_BACK)]
            ],
            one_time_keyboard=False,
            resize_keyboard=True,
        ),
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        parse_mode=ParseMode.HTML,
        text=TEXT_BOT_GREETINGS,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_RIGHTS),
                                  callback_data=f"{CALLBACK_BUTTON_CHECK_RIGHTS}")],
            [InlineKeyboardButton(text=str(BUTTON_CONNECT_TO_PERSON), url=COORDINATOR_LINK)],
            [InlineKeyboardButton(text=str(BUTTON_GET_GIFT), callback_data=f"{BUTTON_GET_GIFT}")],
            [InlineKeyboardButton(text=str(BUTTON_GO_TO_SITE), url=('%s' % SITE_LINK))]
        ])
    )

    return None


async def action_gift_info(update: Update, context: CallbackContext):
    await context.bot.send_message(
        update.effective_user.id,
        "%s" % TEXT_GIFT_INSTRUCTIONS,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=("%s" % BUTTON_DOWNLOAD_APP), url=(LINK_DOWNLOAD_APP))],
            [InlineKeyboardButton(text=('%s' % BUTTON_READY_TO_GET_CODE), url=('%s' % COORDINATOR_LINK))],
        ]))

    return None


async def action_to_check_rights_step_1(update: Update, context: CallbackContext):
    await context.bot.send_message(
        update.effective_user.id,
        TEXT_STEP_1_WELCOME_STEP,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text=str(CALLBACK_BUTTON_YES), callback_data=f"{CALLBACK_BUTTON_YES}"),
                InlineKeyboardButton(text=str(CALLBACK_BUTTON_NO), callback_data=f"{CALLBACK_BUTTON_NO}")
            ],
            [InlineKeyboardButton(text=str(CALLBACK_BUTTON_DONT_KNOW), callback_data=f"{CALLBACK_BUTTON_DONT_KNOW}")],
        ]))

    return CHECK_RIGHT_STEP_1


async def action_check_age(update: Update, context: CallbackContext):
    first_number_match = re.search(r'\d+', update.message.text)

    if not first_number_match:
        await update.message.reply_html(
            "%s" % TEXT_WAITING_FOR_AGE_INPUT
        )
        return None

    first_number = int(first_number_match.group(0))
    await update.message.reply_html(
        TEXT_YOUP_PICKED_AGE % first_number,
    )

    if first_number < 17 or first_number > 40:
        await update.message.reply_html(
            TEXT_STEP_1_PROGRAMS_DENIED,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
                [InlineKeyboardButton(text=str(BUTTON_CONNECT_TO_PERSON), url=COORDINATOR_LINK)]

            ])
        )

    if first_number in range(17, 31):
        await update.message.reply_html(
            "%s" % TEXT_STEP_1_PROGRAMS_17_31,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=('%s' % BUTTON_MASA_4_6_MONTHS), url=('%s' % LINK_ALL_PROGRAMS))],
                [InlineKeyboardButton(text=('%s' % BUTTON_ONWARD_CAMPUS), url=('%s' % LINK_ONWARD_CAMPUS))],
                [InlineKeyboardButton(text=('%s' % BUTTON_ONWARD_VOLONTEERING), url=('%s' % LINK_ONWARD_VOLONTEERING))],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ])
        )

    if first_number in range(31, 35):
        await update.message.reply_html(
            "%s" % TEXT_STEP_1_PROGRAMS_31_35,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=BUTTON_MASA_4_6_MONTHS, url=('%s' % LINK_ALL_PROGRAMS))],
                [InlineKeyboardButton(text=BUTTON_ONWARD_VOLONTEERING, url=('%s' % LINK_ONWARD_VOLONTEERING))],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],

            ])
        )

    if first_number in range(35, 41):
        await update.message.reply_html(
            TEXT_STEP_1_PROGRAMS_35_41,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=BUTTON_ONWARD_VOLONTEERING, url=('%s' % LINK_ONWARD_VOLONTEERING))],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_CHECK_NEW_AGE),
                                      callback_data=f"{CALLBACK_BUTTON_CHECK_NEW_AGE}")],
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ])
        )

    return None


async def callback_action_check_age_again(update: Update, context: CallbackContext) -> Optional[int]:
    answer = update.callback_query.data

    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))

    if answer == CALLBACK_BUTTON_CHECK_NEW_AGE:
        await context.bot.send_message(
            update.effective_user.id,
            "%s" % TEXT_STEP_2_HOW_OLD_ARE_YOU,
            parse_mode=ParseMode.HTML,
        )

    return CHECK_RIGHT_STEP_2


async def action_step_1_answer(update: Update, context: CallbackContext) -> Optional[int]:
    answer = update.callback_query.data

    await update.callback_query.answer()
    await update.callback_query.delete_message()

    if answer == CALLBACK_BUTTON_YES:
        await context.bot.send_message(
            update.effective_user.id,
            "%s" % TEXT_STEP_2_HOW_OLD_ARE_YOU,
            parse_mode=ParseMode.HTML,
        )
        return CHECK_RIGHT_STEP_2

    if answer == CALLBACK_BUTTON_NO:
        await context.bot.send_message(
            update.effective_user.id,
            TEXT_STEP_1_NO_ROOTS,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ]),
            parse_mode=ParseMode.HTML,
        )
        return None

    if answer == CALLBACK_BUTTON_DONT_KNOW:
        await context.bot.send_message(
            update.effective_user.id,
            TEXT_STEP_1_IDK,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=str(CALLBACK_BUTTON_START_AGAIN),
                                      callback_data=f"{CALLBACK_BUTTON_START_AGAIN}")],
            ]),
            parse_mode=ParseMode.HTML,
        )
        return None

    return None

states: dict[object, list[BaseHandler]] = {
        CHECK_RIGHT_STEP_1: [
            CallbackQueryHandler(action_step_1_answer,
                                 pattern=rf"{CALLBACK_BUTTON_YES}|{CALLBACK_BUTTON_NO}|{CALLBACK_BUTTON_DONT_KNOW}"),
        ],
        CHECK_RIGHT_STEP_2: [
            MessageHandler(filters.Regex(f"^{BUTTON_BACK}$"), action_welcome),
            MessageHandler(filters.TEXT, action_check_age),
        ]
    }

conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(action_to_check_rights_step_1, pattern=rf"{CALLBACK_BUTTON_CHECK_RIGHTS}"),
        MessageHandler(filters.Regex(f"^{BUTTON_CHECK_RIGHTS}$"), action_to_check_rights_step_1),
        CallbackQueryHandler(callback_action_check_age_again,
                             pattern=rf"{CALLBACK_BUTTON_CHECK_NEW_AGE}"),
    ],
    states=states,
    fallbacks=[],
    allow_reentry=True,
    name=("%s" % CONVERSATION_NAME),
    per_chat=False,
    per_message=False,
)


def register_handlers(app: telegram.ext.Application):
    app.add_handler(CommandHandler("start", action_welcome))
    app.add_handler(MessageHandler(filters.Regex(f"^{BUTTON_GET_GIFT}$"), action_gift_info))
    app.add_handler(CallbackQueryHandler(action_gift_info, pattern=rf"{BUTTON_GET_GIFT}"))
    app.add_handler(CallbackQueryHandler(action_welcome, pattern=rf"{CALLBACK_BUTTON_START_AGAIN}"))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT, action_welcome))
    app.add_error_handler(error_handler)
