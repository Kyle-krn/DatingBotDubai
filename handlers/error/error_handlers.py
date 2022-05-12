import sys
from loader import dp
from aiogram.utils import exceptions
import logging

import traceback

@dp.errors_handler()
async def error_handler(update, exception: Exception):
    if isinstance(exception, exceptions.CantDemoteChatCreator):
        logging.exception("Can't demote chat creator")
        return True

    if isinstance(exception, exceptions.MessageNotModified):
        logging.exception("Message is not modified")
        return True

    if isinstance(exception, exceptions.MessageToDeleteNotFound):
        logging.exception("Message to delete not found")
        return True

    if isinstance(exception, exceptions.MessageTextIsEmpty):
        logging.exception("MessageTextIsEmpty")
        return True

    if isinstance(exception, exceptions.Unauthorized):
        logging.exception(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, exceptions.InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \n')
        return True

    if isinstance(exception, exceptions.TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \n')
        return True

    if isinstance(exception, exceptions.RetryAfter):
        logging.error(f'RetryAfter: {exception} \n')
        return True

    if isinstance(exception, exceptions.CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \n')
        return True

    if isinstance(exception, exceptions.MessageCantBeDeleted):
        logging.exception("Message cant be deleted")
        return True
    
    logging.exception(f'{exception}')
    return True