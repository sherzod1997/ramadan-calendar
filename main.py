from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters)

from conf import TOKEN, DB_NAME
from db_helper import DBHelper

BTN_TODAY, BTN_TOMORROW, BTN_MONTH, BTN_REGION, BTN_DUA = (
    '⌛️ Bugun', '⏳ Ertaga', '📅 Tuliq taqvim', '🇺🇿 Viloyat', '🤲 Duo')
main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY], [BTN_TOMORROW, BTN_MONTH], [BTN_REGION], [BTN_DUA]
], resize_keyboard=True)

STATE_REGION = 1
STATE_CALENDAR = 2

user_region = dict()
db = DBHelper(DB_NAME)


def region_buttons():
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons


def start(update, context):
    user = update.message.from_user
    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_html(
        'Assalamu aleykum <b>{}!</b>\n \n<b>Ramazon oyi muborak bulsin!</b>\n \nSizga qaysi viloyat buyicha malumot kerak?'.
            format(user.first_name), reply_markup=InlineKeyboardMarkup(buttons))

    return STATE_REGION


def inline_callback(update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        user_region[user_id] = int(query.data)
        query.message.delete()
        query.message.reply_html(text='<b>Ramazon taqvimi</b> 2️⃣0️⃣2️⃣0️⃣\n \nQuyidagilardan birini tanlang 👇',
                                 reply_markup=main_buttons)

        return STATE_CALENDAR
    except Exception as e:
        print('error ', str(e))


def calendar_today(update, context):
    try:
        user_id = update.message.from_user.id
        
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        today = str(datetime.now().date())
        
        print('region', region_id)
        today = '/'.join(str(today).split('-')[::-1])
        print('today',today)
        calendar = db.get_calendar_by_region(region_id, today)
        print('calendar',calendar)
        photo_path = 'images/{}.jpg'.format(calendar['id'])
        message = '<b>Ramazon</b> 2020\n<b>{}</b> vaqti\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5])

        update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                                   reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def calendar_tomorrow(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        dt = str(datetime.now().date() + timedelta(days=1))
        dt = '/'.join(str(dt).split('-')[::-1])
        print('dt',dt)
        print('dt',dt)
        calendar = db.get_calendar_by_region(region_id, dt)
        photo_path = 'images/{}.jpg'.format(calendar['id'])
        message = '<b>Ramazon</b> 2020\n<b>{}</b> vaqti\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5])

        update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                                   reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def calendar_month(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)

        photo_path = 'images/table/region_{}.jpg'.format(region['id'])
        message = '<b>Ramazon</b> 2020\n<b>{}</b> vaqti'.format(region['name'])

        update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                                   reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def select_region(update, context):
    buttons = region_buttons()
    update.message.reply_text('Sizga qaysi viloyat buyicha maulumot kerak?',
                              reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION


def select_dua(update, context):
    saharlik = "<b>Saharlik (ogiz yopish) duosi:</b>\nНавайту ан асума совма шаҳри Рамазона минал фажри илал мағриби, холисан лиллаҳи таъала."
    iftorlik = "<b>Iftorlik (ogiz ochish) duosi:</b>\nАллоҳумма лака сумту ва бика аманту ва аъалайка таваккалту ва ъала ризқика афтарту, фағфирли, йа Ғоффару, ма қоддамту вама аххорту."
    update.message.reply_photo(photo=open('images/ramadan_dua.png', 'rb'),
                               caption="{}\n \n{}".format(saharlik, iftorlik), parse_mode='HTML',
                               reply_markup=main_buttons)


def main():
  
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

 

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [
                CallbackQueryHandler(inline_callback),
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua)

            ],
            STATE_CALENDAR: [
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


main()