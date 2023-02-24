class Num2Text:
    BILLIONS = {
        'forms': ('миллиард', 'миллиарда', 'миллиардов',),
        'gender': 0
    }

    MILLIONS = {
        'forms': ('миллион', 'миллиона', 'миллионов',),
        'gender': 0
    }

    THOUSANDS = {
        'forms': ('тысяча', 'тысячи', 'тысяч',),
        'gender': 1
    }

    RUBLES = {
        'forms': ('рубль', 'рубля', 'рублей',),
        'gender': 0
    }

    KOPEKS = {
        'forms': ('копейка', 'копейки', 'копеек',),
        'gender': 1
    }

    HUNDREDS = ['', 'сто', 'двести', 'триста', 'четыреста', 'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот']

    DOZENS = ['двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто']

    ONES = [('', ''), ('один', 'одна'), ('два', 'две'), ('три', 'три'), ('четыре', 'четыре'), ('пять', 'пять'),
             ('шесть', 'шесть'), ('семь', 'семь'), ('восемь', 'восемь'), ('девять', 'девять'), ('десять', 'десять'),
             ('одиннадцать', 'одиннадцать'), ('двенадцать', 'двенадцать'), ('тринадцать', 'тринадцать'),
             ('четырнадцать', 'четырнадцать'), ('пятнадцать', 'пятнадцать'), ('шестнадцать', 'шестнадцать'),
             ('семнадцать', 'семнадцать'), ('восемнадцать', 'восемнадцать'), ('девятнадцать', 'девятнадцать')]

    RUBLE_FLOW = [RUBLES, THOUSANDS, MILLIONS, BILLIONS]
    KOPEK_FLOW = [KOPEKS]

    def __init__(self, number: float):
        self.__rubles = int(number)
        self.__kopeks = round(number * 100) % 100

    @staticmethod
    def __chunked_number(number):
        result = list()
        while number:
            result.append(number % 1000)
            number = number // 1000
        return result

    @staticmethod
    def __get_form(number, rules):
        if number == 1:
            return rules['forms'][0]
        elif 1 < number < 5:
            return rules['forms'][1]
        return rules['forms'][2]

    def __spell_chunk(self, chunk, rules):
        hundreds = self.HUNDREDS[chunk // 100]
        dozens = chunk % 100 // 10
        if dozens < 2:
            dozens = ''
            ones = chunk % 100
        else:
            dozens = self.DOZENS[dozens - 2]
            ones = chunk % 10
        units = self.__get_form(ones, rules)
        ones = self.ONES[ones][rules['gender']]
        return [hundreds, dozens, ones, units]

    def __spell_part(self, number, flow):
        chunks = self.__chunked_number(number)
        result = list()
        for t, chunk in enumerate(chunks):
            result = self.__spell_chunk(chunk, flow[t]) + result
        return result

    def spell(self):
        spell_list = self.__spell_part(self.__rubles, self.RUBLE_FLOW)
        if self.__kopeks:
            spell_list += self.__spell_part(self.__kopeks, self.KOPEK_FLOW)
        else:
            spell_list.append('ноль копеек')
        spell_list = list(filter(lambda x: x != '', spell_list))
        return ' '.join(spell_list).capitalize()
