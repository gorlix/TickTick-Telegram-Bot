import logging
from typing import Dict

from telegram import __version__ as TG_VER

import secret
import keyboard

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
# ----------------------------------------------------------------------------------------------------------------------


# Enable logging -------------------------------------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
# ----------------------------------------------------------------------------------------------------------------------


# State ----------------------------------------------------------------------------------------------------------------
START, EVENT, SETTINGS, CHOOSING, SAVING, TYPING_CHOICE = range(6)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])
# ----------------------------------------------------------------------------------------------------------------------


# Start ----------------------------------------------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inizia la conversazione e aggiunge la tastiera markup"""
    markup = ReplyKeyboardMarkup(keyboard.start_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Benvenuto, \nscegli cosa aggingere:",
        reply_markup=markup,
    )
    return START
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chiede all'utente la scelta tra inserimento Automatico e manuale"""
    markup = ReplyKeyboardMarkup(keyboard.ins_choise_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Puoi scegliere se aggiungre liberamente i campi o usare l'inserimento Guidato:",
        reply_markup=markup,
    )
    return EVENT
# ----------------------------------------------------------------------------------------------------------------------


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Alcune Impostazioni utili al Bot"""


# Inserimento ----------------------------------------------------------------------------------------------------------
async def add_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chiede all'utente di aggiungere il dettaglio richiesto"""
    markup = ReplyKeyboardMarkup(keyboard.add_event_keyboard, one_time_keyboard=True)

    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        f"Aggiugi {text.lower()}",
        reply_markup=markup,
    )

    return SAVING
# ----------------------------------------------------------------------------------------------------------------------


# Aggiunta -------------------------------------------------------------------------------------------------------------
async def save_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Salva l'informazione inserita in Regular_choise all'interno del Dizionario"""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Il tuo Evento"
        f"{facts_to_str(user_data)}",
    )

    return CHOOSING
# ----------------------------------------------------------------------------------------------------------------------


# Done -----------------------------------------------------------------------------------------------------------------
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chiude la chat con il bot e DEBUG Mostra i dati salvati """
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"{facts_to_str(user_data)} \nPremi /start per Riavviare il BOT ",
        reply_markup=ReplyKeyboardRemove(),  # Rimuove la Tastiera virtuale
    )
    user_data.clear()
    return ConversationHandler.END
# ----------------------------------------------------------------------------------------------------------------------


# Main -----------------------------------------------------------------------------------------------------------------
def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(secret.TELEGRAM_API_KEY).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [
                MessageHandler(
                    filters.Regex("^(Aggiungi Evento)$"), add_event
                ),
                MessageHandler(
                    filters.Regex("^(Indietro)$"), start
                )
                # TODO Settings
                # filters.Regex("^(Impostazioni)$"), settings
            ],
            EVENT: [
                MessageHandler(
                    filters.Regex("^(Indietro)$"), start
                ),
                # TODO Automatic Insert
                # filters.Regex("^(Automatico)$"), automatic_insert,
                # TODO Manual Insert
                # filters.Regex("^(Manuale)$"), manual_insert
            ],
            SETTINGS: [
                # TODO API TOKEN TickTick
                # TODO Lingue
            ],
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Titolo|Descrizione|Data|Ora|Priorità|Categoria|)$"), add_field
                ),
                # TODO Save -> TickTick Upload
            ],
            SAVING: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Fine")), save_field,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Esci"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
