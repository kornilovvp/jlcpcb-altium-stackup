# Заметки по стекам JLCPCB для Altium

Подробные рабочие заметки к репозиторию. Краткое описание и порядок использования см. в `README.md`.

Проверено 2026-10-14: все файлы сверены слой за слоем с ответом API JLCPCB
(`data/jlc_8L_1.6mm_outer1oz_inner0.5oz_templates.json`) скриптом `tools/verify_stackup.py`, 0 расхождений.

| Файл | Шаблон JLC | Итого без маски | Назначение |
|------|------------|-----------------|------------|
| `jlcpcb_8L_1.6mm_outer1oz_inner0.5oz_JLC08161H-2116.stackup` | JLC08161H-2116 (default) | 1.5996 mm | дифпара 100 Ом на L3 при w 0.13 / g 0.20 mm, без доплаты |
| `jlcpcb_8L_1.6mm_outer1oz_inner0.5oz_JLC08161H-7628.stackup` | JLC08161H-7628 | 1.6028 mm | симметричный стек, доплата |
| `jlcpcb_8L_1.6mm_outer1oz_inner0.5oz_JLC08161H-2313.stackup` | JLC08161H-2313 | 1.5236 mm | исторический, для L3 не подходит |

## Стеки

### JLC08161H-2116 (8L, 1.6 mm, 1 oz / 0.5 oz, шаблон по умолчанию)

| Слой | Материал | Толщина, mm | Er |
|------|----------|-------------|----|
| L1 Top | Copper 1 oz | 0.035 | |
| Prepreg | 2116*1 | 0.1164 | 4.16 |
| L2 | Copper 0.5 oz | 0.0152 | |
| Core | 0.30 mm H/HOZ | 0.3 | 4.41 |
| L3 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 1080*1 | 0.0764 | 3.91 |
| Prepreg | 1080*1 | 0.0764 | 3.91 |
| L4 | Copper 0.5 oz | 0.0152 | |
| Core | 0.30 mm H/HOZ | 0.3 | 4.41 |
| L5 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 1080*1 | 0.0764 | 3.91 |
| Prepreg | 1080*1 | 0.0764 | 3.91 |
| L6 | Copper 0.5 oz | 0.0152 | |
| Core | 0.30 mm H/HOZ | 0.3 | 4.41 |
| L7 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 2116*1 | 0.1164 | 4.16 |
| L8 Bottom | Copper 1 oz | 0.035 | |

Итого без маски 1.5996 mm (compressionThickness JLC = 1.5996). Без доплаты, доступен expedited.
Дифпара 100 Ом на L3 (опоры L2/L4): w 0.13 / g 0.20 mm даёт 100.1 Ом по расчёту.

### JLC08161H-7628 (8L, 1.6 mm, 1 oz / 0.5 oz)

| Слой | Материал | Толщина, mm | Er |
|------|----------|-------------|----|
| L1 Top | Copper 1 oz | 0.035 | |
| Prepreg | 7628*1 | 0.2104 | 4.4 |
| L2 | Copper 0.5 oz | 0.0152 | |
| Core | 0.2 mm H/HOZ без меди | 0.2 | 4.36 |
| L3 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 7628*1 | 0.2104 | 4.4 |
| L4 | Copper 0.5 oz | 0.0152 | |
| Core | 0.2 mm | 0.2 | 4.36 |
| L5 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 7628*1 | 0.2104 | 4.4 |
| L6 | Copper 0.5 oz | 0.0152 | |
| Core | 0.2 mm | 0.2 | 4.36 |
| L7 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 7628*1 | 0.2104 | 4.4 |
| L8 Bottom | Copper 1 oz | 0.035 | |

Итого без маски 1.6028 mm. Симметричный стек: 3 ядра, 4 одиночных препрега. В API помечен доплатой (fixedFee 330, coefficient 55), expedited недоступен.

### JLC08161H-2313 (8L, 1.6 mm, 1 oz / 0.5 oz)

| Слой | Материал | Толщина, mm | Er |
|------|----------|-------------|----|
| L1 Top | Copper 1 oz | 0.035 | |
| Prepreg | 2313*1 | 0.0964 | 4.1 |
| L2 | Copper 0.5 oz | 0.0152 | |
| Core | 0.13 mm H/HOZ | 0.13 | 4.17 |
| L3 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 7628*1 | 0.2084 | 4.4 |
| Prepreg | 2313*1 | 0.0964 | 4.1 |
| L4 | Copper 0.5 oz | 0.0152 | |
| Core | 0.30 mm H/HOZ | 0.3 | 4.41 |
| L5 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 2313*1 | 0.0964 | 4.1 |
| Prepreg | 7628*1 | 0.2084 | 4.4 |
| L6 | Copper 0.5 oz | 0.0152 | |
| Core | 0.13 mm | 0.13 | 4.17 |
| L7 | Copper 0.5 oz | 0.0152 | |
| Prepreg | 2313*1 | 0.0964 | 4.1 |
| L8 Bottom | Copper 1 oz | 0.035 | |

Итого без маски 1.5236 mm. В первой версии файла внешние препреги были 0.2083 mm / Er 4.5 (ошибка), исправлено 2026-10-14.

Общее для всех файлов:

- маска 0.015 mm (0.5906 mil), Er 3.8;
- медь L1/L8 1.378 mil (0.035 mm), внутренняя 0.5984 mil (0.0152 mm), материал CF-003 = 0.5 oz по библиотеке Altium;
- LossTangent 0.02, Tg 150C, производитель Nan Ya Plastics NP-155F (справочно, на расчёт не влияет);
- ETCH = Infinity (без подтравы);
- GUID медных слоёв общие для всех файлов, импедансный профиль D100 на месте, Altium пересчитает ширины при открытии.

## Материалы JLCPCB (Nan Ya NP-155F, платы 4–8 слоёв)

Ядра, Er по толщине: 0.08 → 3.99; 0.10 → 4.36; 0.13 → 4.17; 0.15 → 4.36; 0.20 → 4.36; 0.25 → 4.23; 0.30 → 4.41; 0.35 → 4.36;
0.40 → 4.36; 0.45 → 4.36; 0.50 → 4.48; 0.55 → 4.41; 0.60 → 4.36; 0.65 → 4.36; 0.70 → 4.53; более 0.70 → 4.43.

Препреги: 7628 — resin 49 %, 8.6 mil, Er 4.4; 3313 (= 2313, та же толщина и Er) — 57 %, 4.2 mil, Er 4.1; 1080 — 67 %, 3.3 mil, Er 3.91; 2116 — 54 %, 4.9 mil, Er 4.16.
Для 10 слоёв и выше JLC считает по SYTECH S1000-2M.

Параметры калькулятора импеданса JLC: внешняя медь 1 oz = 1.6 mil (с гальваникой), внутренняя 0.5 oz = 0.6 mil, 1 oz = 1.2 mil;
маска базовая 1.2 mil, на меди 0.6 mil, между дорожками 1.2 mil, Er 3.8; верх дорожки = основание минус 0.7 mil.
При заказе с контролем импеданса выбирать материал FR-4 TG155.

## API шаблонов JLCPCB

```
POST https://cart.jlcpcb.com/api/overseas-shop-cart/v1/shoppingCart/getImpedanceTemplateSettings
Content-Type: application/json
{"cuprumThickness":1,"insideCuprumThickness":0.5,"stencilLayer":8,"stencilPly":1.6}
```

Ответ: `data[]` с полями `templateName`, `iaminationList[].content` (JSON-строка слоя: Copper, Prepreg или блок Copper+Core+Copper),
`compressionThickness`, `defaultFlag`, `expeditedFlag`, `fixedFee`, `coefficient` (доплата за шаблон, 0 = без доплаты).
Снимок ответа для 8L 1.6 mm лежит в `data/`. Разбор: `tools/stacks8L.py`.

Все шаблоны 8L 1.6 mm 1 oz / 0.5 oz, диэлектрики вокруг L3 (stripline на L3, опоры L2 и L4):

| Шаблон | L2–L3, mm | L3–L4, mm | Симметрия | Доплата fixedFee / coeff | Expedited |
|--------|-----------|-----------|-----------|--------------------------|-----------|
| 2116 (default) | core 0.30 | 1080 x2 = 0.153 | 0.51 | нет | да |
| 2313 | core 0.13 | 7628 + 2313 = 0.305 | 0.43 | нет | да |
| 3313 | core 0.10 | 2116 x3 = 0.357 | 0.28 | нет | да |
| 2313A | core 0.15 | 2116 x3 = 0.366 | 0.41 | нет | да |
| 2116C | core 0.13 | 2116 x3 = 0.366 | 0.36 | нет | да |
| 7628 | core 0.20 | 7628 = 0.210 | 0.95 | 330 / 55 | нет |
| 2116B | core 0.13 | 2116 = 0.109 | 0.84 | нет | нет |
| 1080A | core 0.10 | 7628 + 1080 + 7628 = 0.505 | 0.20 | 550 / 110 | нет |
| 1080 | core 0.30 | 7628 = 0.210 | 0.70 | 330 / 55 | нет |
| 2116A | core 0.25 | 2116 x2 = 0.233 | 0.93 | 550 / 110 | нет |
| 1080C | core 0.075 | 7628 + 1080 + 7628 = 0.505 | 0.15 | нет | нет |
| 1080B | core 0.15 | 2116 x3 = 0.357 | 0.42 | нет | нет |

## Расчёт: дифпара 100 Ом на L3, опоры L2 и L4

2D-решатель `tools/zdiff_fd.py` (конечные разности, прямоугольная дорожка 0.0152 mm, без потерь, сетка 5 µm).
Проверка на симметричной stripline h = 0.2/0.2, Er 4.4: расхождение с IPC-2141 в пределах 1–4 %.
Калькулятор JLC (трапеция, верх минус 0.7 mil) даст немного другие числа, перед заказом проверить в нём.

| Шаблон | w при зазоре 0.15 mm | w при зазоре 0.20 mm | Zdiff при w 0.13 / g 0.20 |
|--------|----------------------|----------------------|---------------------------|
| 2116A | 125 µm | 150 µm | 105.4 Ом |
| 1080 | 117 µm | 142 µm | 103.2 Ом |
| 2116 (default) | 111 µm | 130 µm | 100.1 Ом |
| 2313A | 108 µm | 128 µm | 99.3 Ом |
| 1080B | 108 µm | 127 µm | 99.2 Ом |
| 7628 | 107 µm | 127 µm | 99.1 Ом |
| 2116C | 103 µm | 120 µm | 96.8 Ом |
| 2313 | 98 µm | 114 µm | 94.8 Ом |
| 3313 | 84 µm | 95 µm | 87.9 Ом |
| 1080A | 82 µm | 94 µm | 87.5 Ом |
| 2116B | 77 µm | 85 µm | 82.5 Ом |
| 1080C | 64 µm | 72 µm | 77.5 Ом |

Вывод для геометрии 0.13 / 0.20 mm: без доплаты и со срочным изготовлением подходит 2116 (default, 100.1 Ом);
самые симметричные стеки 7628 (99.1 Ом) и 2116A, но у них доплата и нет expedited.

## Altium Designer

1. Design » Layer Stack Manager (клавиши D, K) → File » Load Stackup from File → выбрать `.stackup` → Ctrl+S в документе LSM.
2. Вкладка Impedance: профили, у каждого слоя Top Ref / Bottom Ref. В правилах Routing Width и Differential Pairs Routing включить Use Impedance Profile.
3. Не кликать ячейку Weight у меди: толщина сбросится с 0.0152 на номинал 0.0175 mm.
4. Не включать Library Compliance: материалов JLC в библиотеке Altium нет.
5. Библиотека материалов Altium: `System\MaterialLibrary\Data\AltiumLibrary.xml` в папке установки (CF-002 0.33 oz, CF-003 0.5 oz, CF-004 1 oz).

## Via-in-pad (JLCPCB)

Заказ → поле Via Covering → Epoxy Filled & Capped (смола, сверху медь и финиш, IPC-4761 Type VII).
Для 6 и более слоёв стоит по умолчанию и входит в цену, для 2 и 4 слоёв доплата и несколько дней.
Отверстие via не больше 0.5 mm (диапазон 0.15–0.55), рекомендуемо 0.2–0.3 mm при площадке 0.45–0.5 mm, для BGA минимум 0.2 / 0.35 mm.
Действует на всю плату, выборочно не делают. Под BGA брать ENIG. Включать Confirm Production File.
Copper Paste Filled & Capped — то же с проводящей пастой, для тепловых via, дороже.

## PoE на тех же парах (24 В, 15 Вт = 0.625 А)

- DC течёт только на участке RJ45 → линейная обмотка трансформатора → центральный отвод → PoE-схема. На стороне PHY DC нет.
- Две пары: 0.625 А на пару, 0.31 А на дорожку. Четыре пары: вдвое меньше.
- Дорожка L3 0.13 mm / 0.5 oz при 0.31 А: 0.087 Ом/см, на 3 см 82 mV и ~54 °C по IPC-2221 (консервативно). При 0.16 А ~11 °C.
- Решение: RJ45 с встроенной PoE-магнетикой (802.3at/bt), либо участок RJ45–трансформатор на внешнем слое без via: L1 над L2 в стеке 2116,
  100 Ом при g 0.20 mm → w ≈ 0.148 mm (медь 0.04 mm), 0.03 Ом/см, ~2 °C. Центральные отводы ≥ 0.5 mm на 1 oz.
- Магнетика с рейтингом DC через отвод ≥ 0.625 А на пару (802.3bt 1 А). Синфазный дроссель в DC-путь на линейной стороне не ставить.
- Под участком RJ45–магнетика на L2/L4 островок chassis-земли (Bob Smith 4 × 75 Ом + конденсатор 1–2 кВ), зазор ≥ 2 mm до системной земли на всех слоях.
  PoE-возврат и PD-контроллер в изолированной зоне, DC-DC изолированный, если есть другие внешние разъёмы.
- Вход PoE: TVS, предохранитель, мост на Шоттки или активный (на обычном мосте 0.6–0.9 Вт тепла).

## Инструменты

- `tools/build_stackup.py api.json JLC08161H-xxxx donor.stackup out.stackup` — сборка файла любого шаблона из API: заголовок, маска и медные слои (с GUID) берутся из донора, диэлектрики строятся по API с Er NP-155F.
- `tools/verify_stackup.py api.json JLC08161H-xxxx file.stackup` — проверка файла против API: порядок, толщины, Er, сумма, LAYERID, ссылки импедансных профилей.
- `tools/stacks8L.py` — разбор JSON API в список слоёв с Er по таблице NP-155F.
- `tools/zdiff_fd.py` — решатель импеданса (`zdiff`, `z0`, `find_w`), нужны numpy и scipy.
- `tools/update_stackup.py`, `tools/fix_2313.py` — первые одноразовые скрипты (2313 → 7628, исправление 2313), заменены `build_stackup.py`.
- Новый шаблон: `curl` к API (см. выше) → `build_stackup.py` → `verify_stackup.py` → строка в таблицу файлов.
- Запуск: `python -I script.py ...`; при `-I` добавить путь к папке tools в `sys.path`.

## Ссылки

- Заказ и таблицы стеков: https://cart.jlcpcb.com/quote (Layer Stackup → шаблоны)
- Калькулятор импеданса: https://jlcpcb.com/pcb-impedance-calculator
- Руководство по калькулятору: https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator
- Via Covering: https://jlcpcb.com/help/article/pcb-via-covering
- Возможности производства: https://jlcpcb.com/capabilities/pcb-capabilities
- Via-in-pad и BGA: https://jlcpcb.com/blog/via-filling-guide и https://jlcpcb.com/blog/technical-guidance-bga-design-rules
- FPC impedance (только для гибких плат): https://jlcpcb.com/help/article/fpc-impedance-trace-width-spacing
- Автогенерированные стеки JLC для Altium и KiCad (562 файла, формат .stackupx): https://github.com/gsuberland/jlcpcb_autogenerated_stackups
- Altium Layer Stack Manager: https://www.altium.com/documentation/altium-designer/pcb-dlg-layerstackmanagerlayer-stack-manager-ad
