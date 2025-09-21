# parser/scrape_group.py
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
from datetime import date as D
import hashlib, json, re

BASE = "https://cacs.spa.msu.ru/time-table/group?type=0"

def _hash(obj) -> str:
    return hashlib.md5(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def _norm_date(dstr):
    if isinstance(dstr, str) and re.match(r"\d{2}\.\d{2}\.\d{4}", dstr):
        dd, mm, yy = dstr.split(".")
        return D(int(yy), int(mm), int(dd))
    return None

def scrape_group_schedule(
    faculty_label: str,  # "Магистратура"
    course_label: str,   # "1"
    group_label: str,    # "ГМУ-1-2-УЭФ"
    date_from: D,
    date_to: D,
):
    print(f"Scraping schedule for {group_label} ({faculty_label}, {course_label}) from {date_from} to {date_to}")
    with sync_playwright() as p:
        try:
            # Запуск браузера с логированием
            print("Launching Chromium browser...")
            browser = p.chromium.launch(headless=False, slow_mo=300, args=["--no-sandbox", "--remote-debugging-port=9222"])
            page = browser.new_page()

            page.goto(BASE, wait_until="domcontentloaded")
            print(f"Page loaded: {BASE}")
        
            try:
                print("Waiting for loading indicator to disappear...")
                page.wait_for_selector("text=Идет загрузка...", state="detached", timeout=30000)
                print("Loading completed, proceeding with selection...")
            except PwTimeout:
                print("Timeout waiting for the loading indicator (it disappeared too quickly).")

            # Выбор факультета
            select_by_label(faculty_label, "Факультет", page)
            select_by_label(course_label, "Курс", page)
            select_by_label(group_label, "Группа", page)

            # Если есть кнопка "Показать" — нажмём
            btn = page.locator("button:has-text('Показать')")
            if btn.count(): 
                print("Clicking the 'Show' button...")
                btn.click()

            # Ждём, пока загрузится таблица
            print("Waiting for the table to load...")
            page.wait_for_selector(".lessons-table, .schedule, table", timeout=30000)

            # Сбор строк
            rows = page.locator("tr.lesson, .lesson-row, table tr")
            lessons = []
            print(f"Found {rows.count()} rows, scraping data...")

            for i in range(rows.count()):
                r = rows.nth(i)
                txt = r.inner_text().strip()
                if not txt or len(txt.split()) < 3:
                    continue

                def pick(*sels):
                    for s in sels:
                        loc = r.locator(s)
                        if loc.count():
                            return loc.inner_text().strip()
                    return None

                # Сбор данных о паре
                d = pick(".date", "td.date", "[data-col=date]")
                if not d:
                    m = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", txt)
                    d = m.group(1) if m else None

                starts_at = pick(".start", "td.start", "[data-col=start]")
                all_times = re.findall(r"\b([01]\d|2[0-3]):[0-5]\d\b", txt or "")
                ends_at = pick(".end", "td.end", "[data-col=end]") or (all_times[1] if len(all_times) > 1 else None)

                subj = pick(".subject", "td.subject", "[data-col=subject]")
                tchr = pick(".teacher", "td.teacher", "[data-col=teacher]")
                room = pick(".room", "td.room", "[data-col=room]")
                typ  = pick(".type", "td.type", "[data-col=type]")

                pair_raw = pick(".pair-number", "td.pair", "[data-col=pair]") or ""
                m = re.search(r"\b([1-6])\b", pair_raw)
                pair_number = int(m.group(1)) if m else None

                payload = {
                    "date": d, "pair_number": pair_number,
                    "starts_at": starts_at, "ends_at": ends_at,
                    "subject": subj, "type": typ,
                    "teacher": tchr, "room": room,
                    "group_id": group_label, "notes": None
                }
                if payload["date"] and (payload["subject"] or payload["teacher"]):
                    payload["id"] = _hash(payload)
                    # фильтр по датам
                    nd = _norm_date(payload["date"])
                    if nd and (date_from <= nd <= date_to):
                        lessons.append(payload)

            print(f"Found {len(lessons)} lessons.")
            browser.close()
            return lessons

        except Exception as e:
            print(f"Error during scraping: {e}")
            return []

def select_by_label(value, label_text, page):
    try:
        print(f"Selecting '{label_text}' value: '{value}'")
        lab = page.locator(f"label:has-text('{label_text}')")
        if lab.count():
            sel = lab.nth(0).locator("xpath=following::select[1]")
            if sel.count():
                sel.select_option(label=str(value))
                print(f"Successfully selected {label_text} = {value}")
                return True
        # запасные варианты
        for css in ["select[name=faculty]", "#faculty",
                    "select[name=course]", "#course",
                    "select[name=group]", "#group", "select"]:
            loc = page.locator(css)
            if loc.count():
                try:
                    loc.select_option(label=str(value))
                    print(f"Successfully selected {label_text} = {value}")
                    return True
                except:
                    continue
        print(f"Could not select {label_text} = {value}")
        return False
    except Exception as e:
        print(f"Error selecting {label_text}: {e}")
        return False
