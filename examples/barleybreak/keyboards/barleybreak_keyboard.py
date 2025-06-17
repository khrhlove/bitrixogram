from typing import List
from bitrixogram.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder


def get_barleybreak_kb(game_state: List[int]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    for i in range(4):
        for j in range(4):
            num = game_state[i * 4 + j]
            text = str(num) if num != 0 else "_"            
            builder.button(text=text, command="move", command_params=num, width=30)
        builder.newline()    
    builder.adjust(4)
    return builder.as_markup()
