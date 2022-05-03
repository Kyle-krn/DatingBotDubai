from datetime import date

async def zodiac_sign(bday: date):
    if date(month=3, day=21, year=bday.year) <= bday <= date(month=4, day=19, year=bday.year):
        return "♈ Овен"
    
    elif date(month=4, day=20, year=bday.year) <= bday <= date(month=5, day=20, year=bday.year):
        return "♉ Телец"
    
    elif date(month=5, day=21, year=bday.year) <= bday <= date(month=6, day=19, year=bday.year):
        return "♊ Близнецы"
    
    elif date(month=6, day=21, year=bday.year) <= bday <= date(month=7, day=22, year=bday.year):
        return "♋ Рак"
    
    elif date(month=7, day=23, year=bday.year) <= bday <= date(month=8, day=22, year=bday.year):
        return "♌ Лев"
    
    elif date(month=8, day=23, year=bday.year) <= bday <= date(month=9, day=22, year=bday.year):
        return "♍ Дева"
    
    elif date(month=9, day=23, year=bday.year) <= bday <= date(month=10, day=22, year=bday.year):
        return "♎ Весы"
    
    elif date(month=10, day=23, year=bday.year) <= bday <= date(month=11, day=21, year=bday.year):
        return "♏ Скорпион"
    
    elif date(month=11, day=22, year=bday.year) <= bday <= date(month=12, day=21, year=bday.year):
        return "♐ Стрелец"
    
    elif (date(month=12, day=22, year=bday.year) <= bday <= date(month=1, day=19, year=bday.year+1)) or  \
         (date(month=12, day=22, year=bday.year-1) <= bday <= date(month=1, day=19, year=bday.year)):
        return "♑ Козерог"
    
    elif date(month=1, day=20, year=bday.year) <= bday <= date(month=2, day=18, year=bday.year):
        return "♒ Водолей"
    
    elif date(month=2, day=19, year=bday.year) <= bday <= date(month=3, day=20, year=bday.year):
        return "♓ Рыбы"
    
    