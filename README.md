# bitrixogram
Простой асинхронный фреймворк для создания чат-бота Bitrix в стиле 'aiogram' с использованием Bitrix24 REST API

Поддерживает Bitrix REST API и вебхуки, требует поддержки JSON формата от сервиса
Работает на Python 3.x

## Документация
Доступна на https://github.com/lxxr/bitrixogram

## Документация по API чат-бота Bitrix24
https://dev.1c-bitrix.ru/learning/course/index.php?COURSE_ID=93&INDEX=Y

https://dev.1c-bitrix.ru/rest_help/index.php

## Зависимости
- aiohttp
- asyncio
- logging

## Установка 
pip install bitrixogram

или 

tar.gz и whl - https://pypi.org/project/bitrixogram/

## Пример:

### Пример структуры проекта
```
├── bot.py
├── handlers
│   ├── any_handler.py
│   └── message_handler.py
├── keyboards
│   └── main_keyboard.py
├── commands
│   └── commands.py
├── config
│   └── config.py
```

### Создание бота и добавление роутеров для обработки сообщений

```python
import asyncio
from aiohttp import ClientSession
import logging

from bitrixogram.core import BitrixBot,WebhookListener,Dispatcher
from handlers import messages_handler, any_handler

import config.settings as config
import commands.commands as reg_commands


async def main():
    # Настройка логирования
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Создание сессии и инициализация бота
    async with ClientSession() as session:
        # Инициализация бота с необходимыми параметрами
        bx= BitrixBot(config.bitrix_bot_endpoint,config.bitrix_bot_auth,config.bitrix_bot_id, session) 
        # Регистрация команд бота
        await bx.register_commands(reg_commands.commands, config.ip_whook_endpoint)
        dp = Dispatcher()
                
        # Добавление роутеров для обработки сообщений
        dp.add_router(messages_handler.message_router(bx)) 	            # первый роутер
        #.....................................................              ....
        dp.add_router(any_handler.any_router(bx))                           # последний роутер 
        
        # Запуск вебхук-сервера
        webhooks = WebhookListener(host=config.server_whook_addr_ip, port=config.server_whook_port, dispatcher=dp)
        await webhooks.start()
        logger.info("Bitrix bot webhook listener started")
        
        # Бесконечный цикл для поддержания работы бота
        while True:
            await asyncio.sleep(3600)
            logging.info("[Bot] Still active...")
 
if __name__ == "__main__":
    asyncio.run(main())
```

### Пример обработчика

```python
from bitrixogram.core import Router,FSMContext,MagicFilter,Message,Command,State,StatesGroup
from bitrixogram.attach import ReplyAttachMarkup, ReplyAttachBuilder, GridLayout
from keyboards.main_keyboard import get_main_kb

# Инициализация фильтра и роутера
F = MagicFilter()
router = Router()

# Определение состояний для FSM (Finite State Machine)
class TestState(StatesGroup):
    test1_state = State()
    test2_state = State()

def any_router(bx):
    # Обработчик для состояния test1_state и текста "test2" или "test3"
    @router.message(TestState.test1_state,((F.text()=="test2") | (F.text()=="test3")))
    async def handle_message_add_event_test_state1(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        state= await fsm.get_state()
        print(f"get state test1: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test - state1"
        )
        await fsm.set_state(TestState.test2_state)
        
    # Обработчик для состояния test2_state и любого текста
    @router.message(TestState.test2_state,(F.text()))        
    async def handle_message_add_event_test_state2(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        state= await fsm.get_state()
        print(f"get state test2: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test - state2"
        )        
        await fsm.clear_state()
        
    # Обработчик для текста "test"
    @router.message(F.text()=="test")
    async def handle_message_add_event_test(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        await fsm.set_state(TestState.test1_state)
        state= await fsm.get_state()
        print(f"set state: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test"
        )
        
    # Обработчик для любого текста
    @router.message(F.text())
    async def handle_message_add_event_other_text(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        await bx.send_message(chat_id, "Any text handler")
        
    # Обработчик для callback-запросов
    @router.callback_query(F.command())
    async def handle_message_add_event_other_command(command:Command, fsm:FSMContext):
        message_id = command.get_message_id()
        builder = ReplyAttachBuilder()

        # Создание различных типов сеток для вложений
        column_layout = builder.grid_column_layout().add_item(name="priority", value="High").add_item(name="Category", value="Task")
        block_layout = builder.grid_block_layout().add_item(name="Description", value="new version of API", width=250).add_item(name="Category", value="Task", width=100)
        line_layout = builder.grid_line_layout().add_item(name="Priority", value="High", color="#ff0000", width=250).add_item(name="Category", value="Task")
        
        # Пример создания вложения с различными элементами
        attach = (builder
            .user(name="John Smith", avatar="{image_link}", link="https://api.bitrix24.com/")
            .link(name="Issue #12345: new API \"Webhook listener\"", link="https://api.bitrix24.com/", desc="release notes", preview="{image_link}", width=1000, height=638)
            .message("API version [B]im 1.1.0[/B]")
            .delimiter(size=200, color="#c6c6c6")
            .grid(column_layout)
            .grid(block_layout)
            .grid(line_layout)
            .image(link="{image_link}", name="img name", preview="{image_preview_link}", width=1000, height=638)
            .file(link="{file_link}", name="image.jpg", size=1500000)
            .build()).to_dict()

        keyboard=get_main_kb()
        await bx.command_answer(command=command,text=f"This is command - {command.get_command_name()}", attach=attach ,keyboard=keyboard)

    return router
```

### Пример клавиатуры

```python
from bitrixogram.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    # Создание клавиатуры с кнопками
    kb = ReplyKeyboardBuilder()
    kb.button(text="-",command="dec")
    kb.button(text="+",command ="inc", bg_color_token="alarm")
    kb.button(text="=",command = "sum", bg_color="#336633", bg_color_token="primary")
    kb.button(text="5",command = "info", bg_color="#336633", bg_color_token="secondary")
    kb.adjust(4)  # Расположение кнопок по 4 в ряд
    return kb.as_markup(resize_keyboard=True)
```

### Пример команд
```python
# Список команд бота с их параметрами
commands = [
              {'COMMAND': 'inc',  'TITLE': '+','PARAMS': 'text' },
              {'COMMAND': 'dec',  'TITLE': '-','PARAMS': 'text' },
              {'COMMAND': 'info', 'TITLE': '?','PARAMS': 'text' },
              {'COMMAND': 'sum',  'TITLE': '=','PARAMS': 'text' } ]
```

### Пример конфигурации
```python
#endpoints  
bitrix_bot_endpoint=" https://xxx.xxx.xxx/rest/xx/xxx/" # Вебхук для REST API
ip_whook_endpoint='http://WEBHOOK_IP_ADDRESS:WEBHOOK_PORT/' # Внешний вебхук-сервер

#webhook server 
server_whook_addr_ip = "LOCAL_SERVER_IP" # Проверьте маршрут от внешнего интерфейса
server_whook_port = LOCAL_SERVER_PORT

#bitrix bot auth and id
bitrix_bot_auth = "YOUR_BOT_AUTH_TOKEN" # Проверьте в настройках бота Bitrix
bitrix_bot_id=BITRIX_BOT_CLIENT_ID # Проверьте в настройках бота Bitrix
```

