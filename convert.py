import sys, zipfile, csv, io, re, xml.etree.ElementTree as ET
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
src, rates_csv, out = sys.argv[1:4]
KEEP_BRANDS={'arte lamp','citilux','crystal lux','divinare','favourite','freya','feron','maytoni','odeon light','lightstar','lumion','stilfort','st luce','voltum'}
KEEP_PARAMS=['Бренд','Коллекция','Высота изделия, мм','Степень защиты','Страна бренда','Гарантия производителя','Страна производства','Материал арматуры','Цвет арматуры','Напряжение, V','Стиль','Мощность лампы, W','Общая мощность, W','Тип цоколя','Цвет плафонов','Материал плафонов','Количество ламп','Место установки','Форма рассеивателя','Вид рассеивателя','Интерьер','Диаметр, мм','Световой поток, lm','Площадь освещения, м2','Пульт ДУ','Цветовая температура','Индекс цветопередачи, Ra','Лампы в комплекте','Цвет свечения','Тип поверхности','Количество плафонов','Тип крепления','Угол рассеивания, °','Серия','Подходит для натяжных потолков','Диаметр врезного отверстия, мм','Высота встраиваемой части, мм','Длина подвеса, мм','Глубина изделия, мм','Направление плафонов','Наличие выключателя','Форма лампочки','Особенность','В комплекте','Тип шинопровода','Количество клавиш','Наличие рассеивателя','Тип подвеса','Сила тока, A','Размещение']
num=lambda s: float((s or '0').replace(',','.').replace(' ','') or 0)
rates={}
for r in csv.reader(open(rates_csv,encoding='utf8')):
    if len(r)>=3 and r[0] and r[0]!='Бренд':
        rates[r[0].strip().lower()]=(num(r[1]),num(r[2]))
missing=KEEP_BRANDS-set(rates); assert not missing, missing
csv.field_size_limit(10**9)
raw=open(src,'rb').read()
try: text=raw.decode('utf-8-sig')
except UnicodeDecodeError: text=raw.decode('cp1251')
rd=csv.reader(io.StringIO(text,newline=''),delimiter=';'); hdr=next(rd)
ix={n:i for i,n in enumerate(hdr)}
base=['Корневая','Артикул','Название товара','Изображения','Цена','Старая цена','Остаток']
header=base+['Параметр: '+p for p in KEEP_PARAMS]; allrows=[]
tot=0
for row in rd:
    tot+=1
    g=lambda n: row[ix[n]].strip() if n in ix and ix[n]<len(row) else ''
    b=g('Бренд').lower()
    if b not in KEEP_BRANDS: continue
    disc,rate=rates[b]
    price=round(num(g('Цена'))*rate); old=round(num(g('Старая цена'))*rate) or ''
    imgs=' '.join(u for u in re.split(r'[;\s]+',g('Изображения')) if u)
    allrows.append([g('Категория'),g('Артикул'),g('Название'),imgs,price,old,int(num(g('Остаток')))]+[g(p) for p in KEEP_PARAMS])
print(tot,len(allrows))
used=[i for i in range(len(header)) if any(r[i] not in ('',None) for r in allrows)]
w=csv.writer(open(out,'w',encoding='utf-8-sig',newline=''),delimiter=';')
w.writerow([header[i] for i in used])
for r in allrows: w.writerow([r[i] for i in used])
print('dropped empty columns:',[header[i] for i in range(len(header)) if i not in used])
