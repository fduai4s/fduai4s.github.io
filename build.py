#!/usr/bin/env python3
"""Generate the bilingual static site from data/profile.json and data/publications.json.

Usage:  python3 build.py
English pages are written to the repository root, Chinese pages to zh/.
Only the Python standard library is needed.
"""
import html
import json
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent
PROFILE = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
PUBS = json.loads((ROOT / "data" / "publications.json").read_text(encoding="utf-8"))
SITE_URL = PROFILE.get("site_url", "").rstrip("/")

LANGS = {
    "en": {"prefix": "", "html": "en", "other": "zh", "switch": "中文", "switch_lang": "zh-CN", "switch_aria": "切换到中文"},
    "zh": {"prefix": "/zh", "html": "zh-CN", "other": "en", "switch": "English", "switch_lang": "en", "switch_aria": "Switch to English"},
}

PAGES = [
    ("home", "/"),
    ("research", "/research/"),
    ("member", "/member/"),
    ("publications", "/publications/"),
    ("contact", "/contact/"),
    ("teaching", "/teaching/"),
]
NAV = ["home", "research", "member", "publications", "contact"]

T = {
    "home": ("Home", "首页"),
    "research": ("Research", "研究"),
    "member": ("Member", "成员"),
    "publications": ("Publications", "论文"),
    "contact": ("Contact", "联系"),
    "teaching": ("Teaching", "教学"),
    "skip": ("Skip to content", "跳到正文"),
    "identity_sub": ("Fudan University", "复旦大学"),
    "footer": ("Hao Zhang Group · Fudan University", "张浩课题组 · 复旦大学"),
    "faculty_page": ("Fudan faculty page ↗", "复旦教师主页 ↗"),
    "news": ("News", "动态"),
    "all_honors": ("All student honors →", "全部学生获奖 →"),
    "hero_alt": ("Illustration of forward analysis and reverse engineering of perovskite solar-cell materials with machine learning.",
                 "机器学习驱动的钙钛矿光伏材料正向分析与逆向设计示意图。"),
    "rep_pubs": ("Representative publications", "代表性论文"),
    "research_desc": ("Our work spans four connected directions, from AI-driven materials discovery to the physics of quantum and non-Hermitian systems.",
                      "课题组的研究围绕以下四个相互关联的方向展开，从 AI 驱动的材料发现到量子材料与非厄米系统的物理。"),
    "awards": ("Awards", "个人获奖"),
    "bio": ("Biography", "个人简介"),
    "honors": ("Student Honors", "学生获奖"),
    "honors_intro": ("Honors received by group members over the years include:", "课题组同学先后荣获的荣誉："),
    "timeline": ("Timeline", "获奖时间线"),
    "members": ("Group Members", "小组成员"),
    "phd": ("Ph.D. Students", "博士研究生"),
    "master": ("Master’s Students", "硕士研究生"),
    "undergrad": ("Undergraduates", "本科生"),
    "phd_one": ("Ph.D. student", "博士生"),
    "master_one": ("Master’s student", "硕士生"),
    "undergrad_one": ("Undergraduate", "本科生"),
    "since": ("since {y}", "{y} 级"),
    "alumni": ("Alumni", "毕业生与去向"),
    "col_name": ("Name", "姓名"),
    "col_year": ("Year", "毕业年份"),
    "col_degree": ("Degree", "学位"),
    "col_honors": ("Honors", "荣誉"),
    "col_next": ("Next position", "去向"),
    "deg_phd": ("Ph.D.", "博士"),
    "deg_master": ("Master’s", "硕士"),
    "deg_bachelor": ("Bachelor’s", "本科"),
    "email": ("Email", "电子邮件"),
    "office": ("Office", "办公地址"),
    "address": ("Mailing address", "通讯地址"),
    "phone": ("Phone", "电话"),
    "join": ("Prospective students", "招生"),
    "join_text": ("We welcome students with backgrounds in artificial intelligence, optics, materials science, physics and microelectronics. Please send an email with your CV and research interests.",
                  "本课题组欢迎人工智能、光学、材料、物理和微电子背景的同学加入。请通过电子邮件发送简历与研究兴趣。"),
    "pub_intro": ("More than 140 SCI papers · 5 ESI highly cited papers · h-index > 42 · over 6,100 citations by others.",
                  "SCI 论文 140 余篇 · 5 篇 ESI 高被引论文 · h-index > 42 · 他引超过 6100 次。"),
    "selected": ("Selected Publications", "代表性论文"),
    "all_pubs": ("All Publications", "全部论文"),
    "search": ("Search", "搜索"),
    "search_ph": ("Title, author or journal", "标题、作者或期刊"),
    "type": ("Type", "类型"),
    "all_types": ("All types", "全部类型"),
    "year": ("Year", "年份"),
    "all_years": ("All years", "全部年份"),
    "hi_only": ("High-impact only", "仅高影响力期刊"),
    "count": ("Showing {n} of {total} entries", "显示 {n} / {total} 条"),
    "empty": ("No publications match these filters.", "没有符合条件的论文。"),
    "clear": ("Clear the filters", "清除筛选"),
    "journal": ("Journal Papers", "期刊论文"),
    "conference": ("Conference Papers", "会议论文"),
    "book": ("Book Chapter", "书籍章节"),
    "patent": ("Patents", "专利"),
    "other": ("Others", "其他"),
    "type_journal": ("Journal", "期刊"),
    "type_conference": ("Conference", "会议"),
    "type_book": ("Book chapter", "书籍章节"),
    "type_patent": ("Patent", "专利"),
    "type_other": ("Other", "其他"),
    "figure": ("Figure", "配图"),
    "media_link": ("News report (in Chinese) ↗", None),
    "teaching_desc": ("Courses taught by Hao Zhang at Fudan University.", "张浩老师在复旦大学讲授的课程。"),
    "not_found": ("Page not found", "页面不存在"),
}

NOTE_LABELS = {
    "high-impact": ("High-impact journal", "高影响力期刊"),
    "esi": ("ESI highly cited paper", "ESI 高被引论文"),
    "cover": ("Cover story", "封面文章"),
    "back-cover": ("Back-cover story", "封底文章"),
    "top-downloaded": ("Top downloaded paper", "高下载论文"),
    "optics-top": ("Top-tier journal in optics", "光学一区"),
    "nsfc-highlight": ("Featured in NSFC research highlights", "基金成果快讯"),
    "vjbo": ("Selected by Virtual Journal for Biomedical Optics", "入选 Virtual Journal for Biomedical Optics"),
    "media": ("Media coverage", "媒体报道"),
}
BADGES = {"high-impact", "esi", "cover", "back-cover", "top-downloaded", "optics-top"}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

SELF_RE = re.compile(r"(?<![A-Za-z])(Hao Zhang|HAO ZHANG|Zhang, Hao(?![A-Za-z]| Zhang)|Zhang, H\.|Zhang H\.|H\. Zhang|H Zhang|张浩)(\**)")


def t(key, lang):
    en, zh = T[key]
    return en if lang == "en" else zh


def esc(s):
    return html.escape(s, quote=True)


def url(lang, path):
    return LANGS[lang]["prefix"] + path


def fmt_date(d, lang, with_year=True):
    parts = d.split("-")
    y = parts[0]
    m = int(parts[1]) if len(parts) > 1 else None
    if lang == "en":
        if m is None:
            return y if with_year else ""
        return f"{MONTHS[m - 1]} {y}" if with_year else MONTHS[m - 1]
    if m is None:
        return f"{y} 年" if with_year else ""
    return f"{y} 年 {m} 月" if with_year else f"{m} 月"


def rich(s):
    """Escape a citation field and render the little LaTeX used on the source page."""
    s = esc(s)
    s = s.replace("$\\beta$", "β")
    s = re.sub(r"\$_(\w+)\$", r"<sub>\1</sub>", s)
    return s


# ---------------------------------------------------------------- layout

def layout(lang, key, path, title, body, description=None):
    L = LANGS[lang]
    other = L["other"]
    current = ' aria-current="page"'
    nav = "\n".join(
        f'        <a href="{url(lang, p)}"{current if k == key else ""}>{t(k, lang)}</a>'
        for k, p in PAGES if k in NAV
    )
    page_title = PROFILE["site_title"][lang] if key == "home" else f"{title} · {PROFILE['site_title'][lang]}"
    desc = description or PROFILE["description"][lang]
    head_extra = []
    for lg in ("en", "zh"):
        hl = "en" if lg == "en" else "zh-CN"
        href = (SITE_URL + url(lg, path)) if SITE_URL else url(lg, path)
        head_extra.append(f'  <link rel="alternate" hreflang="{hl}" href="{href}">')
    if SITE_URL:
        head_extra.append(f'  <link rel="canonical" href="{SITE_URL}{url(lang, path)}">')
        head_extra.append(f'  <meta property="og:url" content="{SITE_URL}{url(lang, path)}">')
        head_extra.append(f'  <meta property="og:image" content="{SITE_URL}/images/hero.jpg">')
    head_extra = "\n".join(head_extra)
    script = '\n  <script src="/assets/js/site.js" defer></script>' if key == "publications" else ""
    year = date.today().year
    return f"""<!doctype html>
<html lang="{L['html']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="theme-color" content="#e2eaf3">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(desc)}">
{head_extra}
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/site.css">{script}
</head>
<body class="page-{key}">
  <a class="skip-link" href="#main-content">{t('skip', lang)}</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="site-identity" href="{url(lang, '/')}">
        <span class="identity-name">{esc(PROFILE['group_name'])}</span>
        <span class="identity-sub">{t('identity_sub', lang)}</span>
      </a>
      <nav class="primary-navigation" aria-label="{'Main navigation' if lang == 'en' else '主导航'}">
{nav}
      </nav>
      <a class="language-switch" href="{url(other, path)}" lang="{L['switch_lang']}" hreflang="{L['switch_lang']}" aria-label="{L['switch_aria']}">{L['switch']}</a>
    </div>
  </header>

<main id="main-content" class="site-container site-main">
{body}
</main>

  <footer class="site-footer">
    <span>© {year} {t('footer', lang)}</span>
    <nav aria-label="{'More information' if lang == 'en' else '更多信息'}">
      <a href="{url(lang, '/teaching/')}">{t('teaching', lang)}</a>
      <a href="{url(lang, '/member/')}#honors">{t('honors', lang)}</a>
      <a href="{esc(PROFILE['source_page'])}">{t('faculty_page', lang)}</a>
      <a href="{esc(PROFILE['github'])}">GitHub ↗</a>
    </nav>
  </footer>
</body>
</html>
"""


# ---------------------------------------------------------------- publications

PUB_BY_ID = {p["id"]: p for p in PUBS["items"]}


def year_group(p):
    if p["type"] == "journal" and p.get("group"):
        return p["group"]
    if p.get("year"):
        return str(p["year"]) if p["year"] >= 2015 else "Before 2015"
    return ""


def group_label(g, lang):
    if g == "Before 2015" and lang == "zh":
        return "2015 年以前"
    return g


def authors_html(s):
    return SELF_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>{m.group(2)}", rich(s))


def notes_html(p, lang):
    out = []
    for n in p.get("notes", []):
        code = n["code"]
        if code == "link":
            label = n["label_en"] if lang == "en" else n["label_zh"]
            out.append(f'<li><a href="{esc(n["url"])}">{esc(label)} ↗</a></li>')
            continue
        en, zh = NOTE_LABELS[code]
        label = en if lang == "en" else zh
        if n.get("detail"):
            label += f" ({n['detail']})"
        cls = ' class="badge"' if code in BADGES else ""
        out.append(f"<li{cls}>{esc(label)}</li>")
    for m in p.get("media", []):
        label = t("media_link", lang) if lang == "en" else f"{m['label']} ↗"
        out.append(f'<li><a href="{esc(m["url"])}">{esc(label)}</a></li>')
    return f'\n  <ul class="publication-notes">{"".join(out)}</ul>' if out else ""


def pub_article(p, lang):
    search = " ".join([p["id"], p["title"], p["authors"], p["venue"]])
    hi = " data-high-impact" if any(n["code"] == "high-impact" for n in p.get("notes", [])) else ""
    figure = ""
    if p.get("figure"):
        figure = (f'\n  <details class="publication-figure"><summary>{t("figure", lang)}</summary>'
                  f'<img src="/images/papers/{esc(p["figure"])}" alt="{esc(p["title"])}" loading="lazy"></details>')
    return f"""<article class="publication" id="{p['id']}" data-publication data-type="{p['type']}" data-group="{esc(year_group(p))}"{hi} data-search="{esc(search)}">
  <h3 class="publication-title"><span class="publication-id">{p['id']}.</span> {rich(p['title'])}</h3>
  <p class="publication-authors">{authors_html(p['authors'])}</p>
  <p class="publication-venue">{rich(p['venue'])}</p>{notes_html(p, lang)}{figure}
</article>"""


def page_publications(lang):
    items = PUBS["items"]
    sel = []
    for s in PUBS["selected"]:
        p = PUB_BY_ID[s["id"]]
        sel.append(f"""<div class="selected-entry">
  <a class="selected-thumb" href="#{p['id']}"><img src="/images/papers/{esc(s['figure'])}" alt="{esc(p['title'])}"></a>
  <div>
    <h3 class="publication-title"><a href="#{p['id']}">{rich(p['title'])}</a></h3>
    <p class="publication-authors">{authors_html(p['authors'])}</p>
    <p class="publication-venue">{rich(p['venue'])}</p>{notes_html(p, lang)}
  </div>
</div>""")

    journal_groups = []
    for p in items:
        if p["type"] == "journal" and p["group"] not in journal_groups:
            journal_groups.append(p["group"])

    sections = []
    years = []
    for g in journal_groups:
        arts = "\n".join(pub_article(p, lang) for p in items if p["type"] == "journal" and p["group"] == g)
        gid = "year-" + g.lower().replace(" ", "-")
        years.append(g)
        sections.append(f'<section class="publication-year" data-publication-group aria-labelledby="{gid}">\n<h2 id="{gid}">{group_label(g, lang)}</h2>\n{arts}\n</section>')
    journal_html = "\n".join(sections)

    def section(kind):
        arts = "\n".join(pub_article(p, lang) for p in items if p["type"] == kind)
        return (f'<section class="pub-section" data-publication-group aria-labelledby="sec-{kind}">\n'
                f'<h2 id="sec-{kind}">{t(kind, lang)}</h2>\n{arts}\n</section>')

    type_opts = "".join(f'<option value="{k}">{t("type_" + k, lang)}</option>' for k in ("journal", "conference", "book", "patent", "other"))
    year_opts = "".join(f'<option value="{esc(y)}">{group_label(y, lang)}</option>' for y in years)
    jump = " ".join(f'<a href="#year-{y.lower().replace(" ", "-")}">{group_label(y, lang)}</a>' for y in years)
    jump += "".join(f' <a href="#sec-{k}">{t(k, lang)}</a>' for k in ("conference", "book", "patent", "other"))

    body = f"""  <h1>{t('publications', lang)}</h1>
  <p class="publication-intro">{t('pub_intro', lang)}</p>

  <section aria-labelledby="selected-heading">
  <h2 id="selected-heading">{t('selected', lang)}</h2>
{chr(10).join(sel)}
  </section>

  <h2 id="all">{t('all_pubs', lang)}</h2>
  <nav class="section-nav" aria-label="{t('year', lang)}">{jump}</nav>
  <form class="publication-filters" id="publication-filters" role="search" hidden>
    <div class="publication-search">
      <label for="publication-query">{t('search', lang)}</label>
      <input type="search" id="publication-query" name="q" placeholder="{t('search_ph', lang)}" autocomplete="off">
    </div>
    <div>
      <label for="publication-type">{t('type', lang)}</label>
      <select id="publication-type" name="type"><option value="">{t('all_types', lang)}</option>{type_opts}</select>
    </div>
    <div>
      <label for="publication-year">{t('year', lang)}</label>
      <select id="publication-year" name="group"><option value="">{t('all_years', lang)}</option>{year_opts}</select>
    </div>
    <div class="filter-check">
      <input type="checkbox" id="publication-hi" name="hi">
      <label for="publication-hi">{t('hi_only', lang)}</label>
    </div>
  </form>
  <p class="publication-count" id="publication-count" role="status" aria-live="polite" data-template="{t('count', lang)}" hidden></p>
  <p class="publication-empty" id="publication-empty" hidden>{t('empty', lang)} <button type="button" class="link-button" id="publication-clear">{t('clear', lang)}</button></p>

  <div id="publication-list">
<section class="pub-section" aria-labelledby="sec-journal">
<h2 class="visually-hidden" id="sec-journal">{t('journal', lang)}</h2>
{journal_html}
</section>
{section('conference')}
{section('book')}
{section('patent')}
{section('other')}
  </div>"""
    return t("publications", lang), body


# ---------------------------------------------------------------- pages

def news_items(entries, lang, with_year=True):
    out = []
    for h in entries:
        d = h["date"]
        out.append(f"""    <li class="news-item">
      <time class="news-date" datetime="{d}">{fmt_date(d, lang, with_year) or '—'}</time>
      <div class="news-text">{h[lang]}</div>
    </li>""")
    return "\n".join(out)


def fill_links(text, lang):
    """Replace {research}/{publications}/{contact} placeholders with language-specific URLs."""
    for k in ("research", "publications", "contact"):
        text = text.replace("{" + k + "}", url(lang, f"/{k}/"))
    return text


def page_home(lang):
    intro = "\n".join(f"<p>{fill_links(p, lang)}</p>" for p in PROFILE["home_intro"][lang])
    # Group news and student honors share the home page list, newest first.
    latest = sorted(PROFILE.get("news", []) + PROFILE["honors"], key=lambda h: h["date"], reverse=True)[:6]
    latest = [dict(h, **{lang: fill_links(h[lang], lang)}) for h in latest]
    body = f"""  <h1 class="visually-hidden">{esc(PROFILE['site_title'][lang])}</h1>
  <figure class="home-hero">
    <img src="/images/hero.jpg" width="1800" height="1012" fetchpriority="high" alt="{t('hero_alt', lang)}">
  </figure>
  <div class="home-introduction">
{intro}
  </div>

  <section class="home-news" aria-labelledby="news-heading">
    <h2 id="news-heading">{t('news', lang)}</h2>
    <ul class="news-list">
{news_items(latest, lang)}
    </ul>
    <a class="more-link" href="{url(lang, '/member/')}#honors">{t('all_honors', lang)}</a>
  </section>"""
    return t("home", lang), body


def page_research(lang):
    areas = []
    nav = []
    for a in PROFILE["research"]:
        c = a[lang]
        nav.append(f'<a href="#{a["id"]}">{esc(c["title"])}</a>')
        items = "\n".join(f"      <li>{esc(i)}</li>" for i in c["items"])
        papers = []
        for pid in a["papers"]:
            p = PUB_BY_ID[pid]
            papers.append(f'        <li><a href="{url(lang, "/publications/")}#{pid}">{rich(p["title"])}</a> <span>· {rich(p["venue"])}</span></li>')
        papers = "\n".join(papers)
        areas.append(f"""  <section class="research-area" id="{a['id']}">
    <figure>
      <img src="/images/papers/{a['figure']}" alt="{esc(a['caption'][lang])}">
      <figcaption>{esc(a['caption'][lang])}</figcaption>
    </figure>
    <div>
      <h2>{esc(c['title'])}</h2>
      <p class="lead">{esc(c['lead'])}</p>
      <ul>
{items}
      </ul>
      <p class="work-heading">{t('rep_pubs', lang)}</p>
      <ul class="work-list">
{papers}
      </ul>
    </div>
  </section>""")
    body = f"""  <h1>{t('research', lang)}</h1>
  <p class="page-description">{t('research_desc', lang)}</p>
  <nav class="section-nav" aria-label="{t('research', lang)}">{' '.join(nav)}</nav>
{chr(10).join(areas)}"""
    return t("research", lang), body


def page_member(lang):
    P = PROFILE
    first, second = (P["name"]["en"], P["name"]["zh"]) if lang == "en" else (P["name"]["zh"], P["name"]["en"])
    bio = "\n".join(f"    <p>{p}</p>" for p in P["bio"][lang])
    awards = "\n".join(f'    <li><span class="year">{a["year"]}</span><span>{a[lang]}</span></li>' for a in P["awards"])
    summary = "\n".join(f"    <li>{s[lang]}</li>" for s in P["honors_summary"])

    timeline = []
    by_year = {}
    for h in P["honors"]:
        by_year.setdefault(h["date"][:4], []).append(h)
    for y, hs in by_year.items():
        label = y if lang == "en" else f"{y} 年"
        timeline.append(f'  <h3 class="timeline-year" id="honors-{y}">{label}</h3>\n  <ul class="news-list">\n{news_items(hs, lang, with_year=False)}\n  </ul>')
    timeline = "\n".join(timeline)

    def card(m):
        a, b = (m["en"], m["zh"]) if lang == "en" else (m["zh"], m["en"])
        role = t(m["group"] + "_one", lang) + " · " + t("since", lang).format(y=m["year"])
        if lang == "zh":
            role = t("since", lang).format(y=m["year"]) + t(m["group"] + "_one", lang)
        if m.get("note"):
            role += " · " + m["note"][lang]
        return f'      <div class="member-card"><h4>{esc(a)}<span lang="{"zh-CN" if lang == "en" else "en"}">{esc(b)}</span></h4><p>{esc(role)}</p></div>'

    groups = []
    for g in ("phd", "master", "undergrad"):
        cards = "\n".join(card(m) for m in P["members"] if m["group"] == g)
        groups.append(f'    <h3>{t(g, lang)}</h3>\n    <div class="people-grid">\n{cards}\n    </div>')
    groups = "\n".join(groups)

    rows = []
    for al in P["alumni"]:
        a, b = (al["en"], al["zh"]) if lang == "en" else (al["zh"], al["en"])
        honors = "".join(f"<li>{h[lang]}</li>" for h in al["honors"])
        honors = f"<ul>{honors}</ul>" if honors else "—"
        nxt = esc(al["next"][lang]) if al.get("next") else "—"
        rows.append(f'      <tr><td class="name">{esc(a)}<span>{esc(b)}</span></td><td>{al["year"]}</td>'
                    f'<td>{t("deg_" + al["degree"], lang)}</td><td>{honors}</td><td>{nxt}</td></tr>')
    rows = "\n".join(rows)

    body = f"""  <section class="person-header" aria-labelledby="pi-name">
    <img class="person-photo" src="/images/hao-zhang.jpg" width="600" height="600" alt="{esc(first)}">
    <div class="person-heading">
      <h1 id="pi-name">{esc(first)}<span class="person-name-zh">{esc(second)}</span></h1>
      <p>{P['title'][lang]}</p>
      <p class="person-affiliation">{P['affiliation'][lang]}</p>
      <p class="person-affiliation">{P['distinction'][lang]}</p>
      <div class="person-links">
        <span>{t('email', lang)}: {esc(P['email_display'])}</span>
        <a href="{url(lang, '/publications/')}">{t('publications', lang)}</a>
        <a href="{url(lang, '/research/')}">{t('research', lang)}</a>
      </div>
    </div>
  </section>

  <nav class="section-nav" aria-label="{t('member', lang)}">
    <a href="#awards">{t('awards', lang)}</a> <a href="#honors">{t('honors', lang)}</a>
    <a href="#members">{t('members', lang)}</a> <a href="#alumni">{t('alumni', lang)}</a>
  </nav>

  <div class="person-bio">
{bio}
  </div>

  <section class="member-section" aria-labelledby="awards">
  <h2 id="awards">{t('awards', lang)}</h2>
  <ul class="plain-list">
{awards}
  </ul>
  </section>

  <section class="member-section" aria-labelledby="honors">
  <h2 id="honors">{t('honors', lang)}</h2>
  <p>{t('honors_intro', lang)}</p>
  <ul class="summary-list">
{summary}
  </ul>
{timeline}
  </section>

  <section class="member-section" aria-labelledby="members">
  <h2 id="members">{t('members', lang)}</h2>
{groups}
  </section>

  <section class="member-section" aria-labelledby="alumni">
  <h2 id="alumni">{t('alumni', lang)}</h2>
  <div class="table-scroll">
  <table>
    <thead><tr><th>{t('col_name', lang)}</th><th>{t('col_year', lang)}</th><th>{t('col_degree', lang)}</th><th>{t('col_honors', lang)}</th><th>{t('col_next', lang)}</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
  </div>
  </section>"""
    return t("member", lang), body


def page_contact(lang):
    C = PROFILE["contact"]
    body = f"""  <h1>{t('contact', lang)}</h1>
  <dl class="contact-list">
    <dt>{t('email', lang)}</dt><dd>{esc(PROFILE['email_display'])}</dd>
    <dt>{t('office', lang)}</dt><dd>{C['office'][lang]}</dd>
    <dt>{t('address', lang)}</dt><dd>{C['address'][lang]}</dd>
    <dt>{t('phone', lang)}</dt><dd>{C['phone'][lang]}</dd>
  </dl>
  <h2>{t('join', lang)}</h2>
  <p>{t('join_text', lang)}</p>"""
    return t("contact", lang), body


def page_teaching(lang):
    groups = []
    for g in PROFILE["teaching"]:
        c = g[lang]
        items = "\n".join(f"    <li>{esc(x)}</li>" for x in c["courses"])
        groups.append(f'  <section class="course-group">\n  <h2>{esc(c["level"])}</h2>\n  <ul>\n{items}\n  </ul>\n  </section>')
    body = f"""  <h1>{t('teaching', lang)}</h1>
  <p class="page-description">{t('teaching_desc', lang)}</p>
{chr(10).join(groups)}"""
    return t("teaching", lang), body


BUILDERS = {
    "home": page_home, "research": page_research, "member": page_member,
    "publications": page_publications, "contact": page_contact, "teaching": page_teaching,
}


def write(rel, content):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print("wrote", rel)


def build():
    for lang in LANGS:
        for key, path in PAGES:
            title, body = BUILDERS[key](lang)
            rel = (LANGS[lang]["prefix"].strip("/") + path).strip("/")
            write(f"{rel}/index.html" if rel else "index.html", layout(lang, key, path, title, body))

    body404 = f"""  <h1>{T['not_found'][0]} · {T['not_found'][1]}</h1>
  <p><a href="/">Home</a> · <a href="/zh/">首页</a></p>"""
    write("404.html", layout("en", "404", "/", T["not_found"][0], body404))

    if SITE_URL:
        urls = [SITE_URL + url(lang, p) for lang in LANGS for _, p in PAGES]
        sm = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
        write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


if __name__ == "__main__":
    build()
