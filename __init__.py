from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler


class GpbNewsSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder().require('GpbNews'))
    def handle_gpb_news(self, message):
        self.speak_dialog('gpb.news')


def create_skill():
    return GpbNewsSkill()

