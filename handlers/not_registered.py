"""
Created by Gotham on 25-08-2018.
"""


class NotRegistered():
    @staticmethod
    def fetchone(c, query, bot):
        if not c.fetchone():
            bot.edit_message_text(text='You are not registered to the bot. Please register using /register command',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return False
        return True
