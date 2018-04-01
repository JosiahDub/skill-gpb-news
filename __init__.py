# built-in
import re
import time
# 3rd party
import feedparser
import requests
# Mycroft stuff
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
try:
    from mycroft.skills.audioservice import AudioService
except:
    from mycroft.util import play_mp3
    AudioService = None

__author__ = 'josiahdub'

LOGGER = getLogger(__name__)


class GPBNewsSkill(MycroftSkill):
    """
    Plays the latest news from Georgia Public Broadcasting

    Shamelessly stolen from the NPR News Skill with a few tweaks.

    Note that the latest mp3 may not be news, but could be an interview, etc.
    If you know a better source for the latest news mp3, let me know.
    """
    def __init__(self):
        super(GPBNewsSkill, self).__init__(name="GPBNewsSkill")
        # This could change at any time and ruin the skill
        self.url_rss = "http://feeds.feedburner.com/gpbnews/GeorgiaRSS?format=xml"
        self.process = None
        self.audioservice = None

    def initialize(self):
        intent = IntentBuilder("GPBNewsIntent").require(
            "GPBNewsKeyword").build()
        self.register_intent(intent, self.handle_intent)

        intent = IntentBuilder("GPBNewsStopIntent") \
            .require("GPBNewsStopVerb") \
            .require("GPBNewsKeyword").build()
        self.register_intent(intent, self.handle_stop)

        if AudioService:
            self.audioservice = AudioService(self.emitter)

    def handle_intent(self, message):
        try:
            self.stop()
            self.speak_dialog("gpb.news")
            # Pause for the intro, then start the new stream
            time.sleep(4)
            feed = feedparser.parse(self.url_rss)
            next_link = feed["entries"][0]["links"][0]["href"]
            html = requests.get(next_link)
            # Find the first mp3 link
            mp3_find = re.search('href="(?P<mp3>.+\.mp3)"', html.content)
            # Replace https with http because AudioService can't handle it
            mp3_link = mp3_find.group("mp3").replace("https", "http")
            # if audio service module is available use it
            if self.audioservice:
                self.audioservice.play(mp3_link, message.data['utterance'])
            else:
                # otherwise use normal mp3 playback
                self.process = play_mp3(mp3_link)
        except Exception as e:
            self.speak_dialog("gpb.news.stop")
            LOGGER.error("Error: {0}".format(e))

    def handle_stop(self, message):
        self.stop()
        self.speak_dialog('gpb.news.stop')

    def stop(self):
        if self.audioservice:
            self.audioservice.stop()
        else:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait()


def create_skill():
    return GPBNewsSkill()

