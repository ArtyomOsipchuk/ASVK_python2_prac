import gettext
import locale

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("TheWorld", "po", ["ru"]),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
}

# gettext.translation(домен, каталог_с_переводами, fallback=True позволяет запускать без перевода
translation = gettext.translation("TheWorld", "po", fallback=True)
_, ngettext = translation.gettext, translation.ngettext

def _(text):
    return LOCALES[locale.getlocale()].gettext(text)

def __(*args):
    return LOCALES[locale.getlocale()].ngettext(*args)

while (c := input(_("InputString> "))):
    for loc in LOCALES:
        locale.setlocale(locale.LC_ALL, loc)
        N = len(c.split())
        print(__("Entered {} word", 'Entered {} words', N).format(N))


# pybabel extract -o prog.pot  .
# pybabel init -D TheWorld -d po -l ru_RU.UTF-8 -i 2.pot
# or (pybabel update -D TheWorld -d po -l ru_RU.UTF-8 -i 2.pot)
# pybabel compile -D TheWorld -d po -l ru_RU.UTF-8
