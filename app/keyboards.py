from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Catalog", callback_data='catalog')],
        [InlineKeyboardButton(text="Basket", callback_data='basket'),
         InlineKeyboardButton(text="Contacts", callback_data='contacts')]
    ]
    # resize_keyboard=True, 
    # input_field_placeholder='Choose:'
)


settings = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text='YouTube', url='https://www.youtube.com/')]
  ])
 


# iz bazy dannyh esli budem delat knopki
cars = ['Tesls', 'Mers', 'BMW']

async def inline_cars():
  keyboard = InlineKeyboardBuilder()
  for car in cars: 
    keyboard.add(InlineKeyboardButton(text=car, callback_data=f'car_{car}'))
  return keyboard.adjust(2).as_markup()