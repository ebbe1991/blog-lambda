import json
from datetime import date, datetime
import urllib.parse

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
    check_daterange(gueltigVonDate, gueltigBisDate)
    return BlogDTO(
        betreff,
        nachricht,
        introtext,
        gueltigVonDate,
        gueltigBisDate,
        item.get('id')
    )


class BlogDTO:

    def __init__(self, betreff: str, nachricht: str, introtext: str, gueltigVon: date, gueltigBis: date, id: str = None):
        if id:
            self.id = id
        else:
            self.id = BlogDTO.create_id(betreff, gueltigVon)
        self.betreff = betreff
        self.nachricht = nachricht
        self.introtext = introtext
        self.gueltigVon = gueltigVon
        self.gueltigBis = gueltigBis
        self.ttl = compute_ttl_for_date(gueltigBis, 7) if getenv_as_boolean(
            'TTL_FEATURE_ACTIVE', True) else None

    def create_id(betreff: str, gueltigVon: date = None):
        if gueltigVon is None:
            gueltigVon = datetime.now()
        return gueltigVon.strftime('%y%m%d')+'_'+urllib.parse.quote(betreff.lower().replace(" ", "-"))

    def to_json(self):
        return json.dumps(self.__dict__, cls=BlogDTOEncoder)


class BlogDTOEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        else:
            return super().default(obj)
