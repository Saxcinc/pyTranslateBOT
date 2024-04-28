from table_models.settings import SessionLocal
from table_models.users import Words, Translations


def add_words():
    translations = {
        "alleviate": "облегчать",
        "anomaly": "аномалия",
        "articulate": "чётко излагать",
        "benevolent": "благожелательный",
        "comprehensive": "всеобъемлющий",
        "conscientious": "добросовестный",
        "contemplate": "размышлять",
        "culminate": "завершаться",
        "detrimental": "вредный",
        "diligent": "прилежный",
        "disseminate": "распространять",
        "eccentric": "эксцентричный",
        "elucidate": "прояснять",
        "empathetic": "сочувствующий",
        "equivocal": "двусмысленный",
        "exacerbate": "усугублять",
        "exemplify": "иллюстрировать",
        "facetious": "шутливый",
        "fleeting": "мимолетный",
        "formidable": "внушительный",
        "gratuitous": "беспричинный",
        "haphazard": "случайный",
        "impetuous": "порывистый",
        "incongruous": "несоответствующий",
        "infallible": "непогрешимый",
        "inquisitive": "любознательный",
        "meticulous": "педантичный",
        "nostalgic": "ностальгический",
        "omniscient": "всеведущий",
        "peripheral": "периферийный",
        "plausible": "правдоподобный",
        "poignant": "трогательный",
        "pragmatic": "прагматичный",
        "precarious": "неустойчивый",
        "quintessential": "архетипичный",
        "reciprocal": "взаимный",
        "redundant": "избыточный",
        "scrutinize": "тщательно изучать",
        "sporadic": "спорадический",
        "substantiate": "подтверждать",
        "superfluous": "излишний",
        "tangible": "осязаемый",
        "tenacious": "упорный",
        "transient": "преходящий",
        "ubiquitous": "вездесущий",
        "unprecedented": "беспрецедентный",
        "vindicate": "оправдывать",
        "vulnerable": "уязвимый",
        "whimsical": "причудливый",
        "zealous": "ревностный", "apple": "яблоко",
        "tree": "дерево",
        "book": "книга",
        "car": "автомобиль",
        "door": "дверь",
        "window": "окно",
        "chair": "стул",
        "desk": "письменный стол",
        "phone": "телефон",
        "flower": "цветок",
        "cat": "кот",
        "dog": "собака",
        "city": "город",
        "mountain": "гора",
        "river": "река",
        "ocean": "океан",
        "beach": "пляж",
        "food": "еда",
        "water": "вода",
        "tea": "чай",
        "coffee": "кофе",
        "house": "дом",
        "garden": "сад",
        "forest": "лес",
        "sky": "небо",
        "star": "звезда",
        "moon": "луна",
        "sun": "солнце",
        "cloud": "облако",
        "rain": "дождь"
    }
    with SessionLocal() as session:
        for key, value in translations.items():
            existing_word = session.query(Words).filter_by(word=key).one_or_none()
            if not existing_word:
                new_word = Words(word=key)
                session.add(new_word)
                session.flush()

                new_translation = Translations(translation=value, word_id=new_word.id)
                session.add(new_translation)
            else:
                print(f"Такое слово '{key}' уже есть в таблице.")
            try:
                session.commit()
            except Exception as ex:
                session.rollback()
                print(ex)
