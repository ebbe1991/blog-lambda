from datetime import datetime, date
from src import blog_dto


def test_simple_id():
    id = blog_dto.BlogDTO.create_id("Mein Text")
    assert id == datetime.now().strftime('%y%m%d')+'_mein-text'


def test_sonderzeichen():
    id = blog_dto.BlogDTO.create_id("Mein-+Text")
    assert id == datetime.now().strftime('%y%m%d')+'_mein-text'


def test_with_date():
    id = blog_dto.BlogDTO.create_id("Mein Text", date(2023, 1, 1))
    assert id == '230101_mein-text'


def test_umlaute():
    id = blog_dto.BlogDTO.create_id("Mein größter Text mit überflüssigen Änderungen!")
    assert id == datetime.now().strftime('%y%m%d')+'_mein-groesster-text-mit-ueberfluessigen-aenderungen'
