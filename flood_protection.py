import time
# CLASS FOR FLOOD PROTECTION


class Spam_settings:
    def __init__(self):
        self.limits = {1: 3, 5: 7, 10: 10, 15: 13, 30: 20}  # max: 3 updates in 1 second, 7 updates in 5 seconds etc
        self.timeout_start = 10
        self.timeout_factor = 5
        self.factors = {}
        self.timeouts = {}
        self.times = {}

    def new_message(self, chat_id):
        update_time = time.time()
        if chat_id not in self.timeouts:
            self.timeouts.update({chat_id: 0})
            self.times.update({chat_id: [update_time]})
            self.factors.update({chat_id: 1})
        else:
            if self.timeouts[chat_id] > update_time:
                return self.timeouts[chat_id] - update_time
            for limit in self.limits:
                amount = 1
                for n, upd_time in enumerate(self.times[chat_id]):
                    if update_time - upd_time < limit:
                        amount += 1
                    else:
                        if amount > self.limits[limit]:
                            self.timeouts[chat_id] = update_time + self.timeout_start * (self.factors[chat_id])
                            self.factors[chat_id] *= self.timeout_factor
                            text = "You are timeouted by the flood protection" \
                                   " system of this bot. Try again in {0} seconds."\
                                .format(self.timeouts[chat_id] - update_time)
                            return text
        self.times[chat_id].insert(0, update_time)
        return 0

    def wrapper(self, func):  # only works on functions, not on instancemethods
        def func_wrapper(bot, update, *args2):
            timeout = self.new_message(update.effective_chat.id)
            if not timeout:
                return func(bot, update, *args2)
            elif isinstance(timeout, str):
                self.message_sender(bot, update, timeout)
        return func_wrapper

    def wrapper_for_class_methods(self, func):  # only works on functions, not on instancemethods
        def func_wrapper(class_obj, bot, update, *args2):
            timeout = self.new_message(update.effective_chat.id)
            if not timeout:
                return func(class_obj, bot, update, *args2)
            elif isinstance(timeout, str):
                self.message_sender(bot, update, timeout)
        return func_wrapper

    @staticmethod
    def message_sender(bot, update, timeout):
        print("timeout")
        # Only works for messages (+Commands) and callback_queries (Inline Buttons)
        if update.callback_query:
            bot.edit_message_text(chat_id=update.effective_chat.id,
                                  message_id=update.effective_message.message_id,
                                  text=timeout)
        elif update.message:
            bot.send_message(chat_id=update.effective_chat.id, text=timeout)