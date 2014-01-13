import unicodedata


def reset_state():
    # reset state

    from .models import StateInfo
    from .models import db

    StateInfo.query.delete()
    db.session.commit()


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')
