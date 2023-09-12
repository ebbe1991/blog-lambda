import json
from datetime import date, datetime
import urllib.parse
import re

from lambda_utils.validation import check_required_field, check_daterange
from lambda_utils.date_utils import compute_ttl_for_date, fromisoformat
from lambda_utils.env_utils import getenv_as_boolean


def create(item: dict):
    betreff = item.get('betreff')
    check_required_field(betreff, 'betreff')
    nachricht = item.get('nachricht')
    check_required_field(nachricht, 'nachricht')
    introtext = item.get('introtext')
    gueltigVon = item.get('gueltigVon')
    gueltigBis = item.get('gueltigBis')
    gueltigVonDate = None if gueltigVon is None else fromisoformat(gueltigVon)
    gueltigBisDate = None if gueltigBis is None else fromisoformat(gueltigBis)
    hasPicture = item.get('hasPicture') or False
    check_daterange(gueltigVonDate, gueltigBisDate)
    return BlogDTO(
        betreff,
        nachricht,
        introtext,
        gueltigVonDate,
        gueltigBisDate,
        hasPicture,
        item.get('id')
    )


class BlogDTO:

    def __init__(self, betreff: str, nachricht: str, introtext: str, gueltigVon: date, gueltigBis: date, hasPicture: bool = False, id: str = None):
        if id:
            self.id = id
        else:
            self.id = BlogDTO.create_id(betreff, gueltigVon)
        self.betreff = betreff
        self.nachricht = nachricht
        self.introtext = introtext
        self.gueltigVon = gueltigVon
        self.gueltigBis = gueltigBis
        self.hasPicture = hasPicture
        self.ttl = compute_ttl_for_date(gueltigBis, 7) if getenv_as_boolean(
            'TTL_FEATURE_ACTIVE', True) else None

    def create_id(betreff: str, gueltigVon: date = None):
        if gueltigVon is None:
            gueltigVon = datetime.now()

        id = remove_special_characters(
            betreff.lower()
            .replace(" ", "-")
            .replace("ä", "ae")
            .replace("ü", "ue")
            .replace("ö", "oe")
            .replace("ß", "ss")
        )
        return gueltigVon.strftime('%y%m%d')+'_'+urllib.parse.quote(id)

    def to_json(self):
        return json.dumps(self.__dict__, cls=BlogDTOEncoder)


def remove_special_characters(input_string):
    # Entfernen Sie alle Zeichen außer Buchstaben, Zahlen und Bindestriche
    cleaned_string = re.sub(r'[^a-zA-Z0-9-]', '', input_string)
    return cleaned_string


class BlogDTOEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        else:
            return super().default(obj)
