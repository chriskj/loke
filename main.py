# coding=UTF-8
import logging

# Import core
from loke import Loke
from config import config

# Import all event handles - comment out the ones you don't need.
# Please note that some of them requires files in data/ to be present
from modules.atb import AtBHandler
from modules.auto_response import AutoResponseHandler
from modules.avinor import AvinorHandler
from modules.brew import BrewHandler
from modules.bysykkel import BysykkelHandler
from modules.chartertur import CharterturHandler
from modules.mannen import MannenHandler
from modules.ruter import RuterHandler
from modules.seen import SeenHandler
from modules.tfl import TfLHandler
from modules.turstatus import TurstatusHandler
from modules.yr import YrHandler
from modules.weather import WeatherHandler


HANDLERS = (
    AtBHandler,
    AutoResponseHandler,
    AvinorHandler,
    BrewHandler,
    BysykkelHandler,
    CharterturHandler,
    MannenHandler,
    RuterHandler,
    SeenHandler,
    TfLHandler,
    TurstatusHandler,
    YrHandler,
    WeatherHandler,
)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    loke = Loke(config).init()

    for handler_class in HANDLERS:
        try:
            handler_class(loke)
        except Exception:
            logging.exception('Could not load module %s', handler_class.__name__)

    loke.loop()
