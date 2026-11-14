import sys, zipfile, csv, io, re, xml.etree.ElementTree as ET
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
src, rates_csv, out = sys.argv[1:4]
KEEP_BRANDS={'arte lamp','citilux','crystal lux','divinare','favourite','freya','feron','maytoni','odeon light','lightstar','lumion','stilfort','st luce','voltum'}
KEEP_PARAMS=['Бренд','Коллекция','Высота изделия, мм','Степень защиты','Страна бренда','Гарантия производителя','Страна производства','Материал арматуры','Цвет арматуры','Напряжение, V','Стиль','Мощность лампы, W','Общая мощность, W','Тип цоколя','Цвет плафонов','Материал плафонов','Количество ламп','Место установки','Форма рассеивателя','Вид рассеивателя','Интерьер','Диаметр, мм','Световой поток, lm','Площадь освещения, м2','Пульт ДУ','Цветовая температура','Индекс цветопередачи, Ra','Лампы в комплекте','Цвет свечения','Тип поверхности','Количество плафонов','Тип крепления','Угол рассеивания, °','Серия','Подходит для натяжных потолков','Диаметр врезного отверстия, мм','Высота встраиваемой части, мм','Длина подвеса, мм','Глубина изделия, мм','Направление плафонов','Наличие выключателя','Форма лампочки','Особенность','В комплекте','Тип шинопровода','Количество клавиш','Наличие рассеивателя','Тип подвеса','Сила тока, A']
num=lambda s: float((s or '0').replace(',','.').replace(' ','') or 0)
rates={}
for r in csv.reader(open(rates_csv,encoding='utf8')):
    if len(r)>=3 and r[0] and r[0]!='Бренд':
        rates[r[0].strip().lower()]=(num(r[1]),num(r[2]))
missing=KEEP_BRANDS-set(rates); assert not missing, missing
def col(r):
    n=0
    for ch in ''.join(c for c in r if c.isalpha()): n=n*26+ord(ch)-64
    return n-1
z=zipfile.ZipFile(src); hdr=None
base=['Корневая','Подкатегория 1','Подкатегория 2','Артикул','Название товара','Краткое описание','Полное описание','Изображения','Цена','Старая цена','Остаток']
w=csv.writer(open(out,'w',encoding='utf-8-sig',newline=''),delimiter=';')
w.writerow(base+['Параметр: '+p for p in KEEP_PARAMS])
tot=kept=0
for ev,el in ET.iterparse(z.open('xl/worksheets/sheet1.xml')):
    if el.tag!=ns+'row': continue
    row={}
    for c in el.findall(ns+'c'):
        t=c.find(ns+'is')
        if t is not None: v=''.join(x.text or '' for x in t.iter(ns+'t'))
        else:
            v=c.find(ns+'v'); v=v.text if v is not None else ''
        row[col(c.get('r'))]=v
    el.clear()
    if hdr is None: hdr={v:k for k,v in row.items()}; continue
    tot+=1
    g=lambda n: row.get(hdr[n],'').strip() if n in hdr else ''
    b=g('Параметр: Бренд').lower()
    if b not in KEEP_BRANDS: continue
    disc,rate=rates[b]
    price=round(num(g('Цена'))*rate); old=round(num(g('Параметр: Старая цена'))*rate) or ''
    w.writerow([g(n) for n in base[:8]]+[price,old,int(num(g('Остаток')))]+[g('Параметр: '+p) for p in KEEP_PARAMS]); kept+=1
print(tot,kept)
