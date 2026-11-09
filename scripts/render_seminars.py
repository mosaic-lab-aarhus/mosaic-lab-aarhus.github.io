"""Rebuild the ready-to-preview seminars page from data/seminars.json."""
from pathlib import Path
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- SEMINAR_CONTENT_START -->'
END = '<!-- SEMINAR_CONTENT_END -->'

def e(value):
    return escape(str(value), quote=True)

def render_row(event, today):
    day = date.fromisoformat(event['date'])
    topic = e(event['topic'])
    if event['topic_kind'] == 'unspecified':
        text = 'To be announced' if day >= today else 'Topic not listed'
        topic_html = f'<span class="note">{text}</span>'
    else:
        kind = 'talk title' if event['topic_kind'] == 'title' else 'suggested reading'
        if event.get('reading_url'):
            topic = f'<a href="{e(event["reading_url"])}">{topic}</a>'
        topic_html = f'<span class="seminar-topic-label">{kind}</span><p>{topic}</p>'
    readings = event.get('additional_readings', [])
    if readings:
        links = ' · '.join(f'<a href="{e(r["url"])}">{e(r["title"])}</a>' for r in readings)
        topic_html += f'<div class="seminar-reading-links">{links}</div>'
    affiliation = event['affiliation'] or 'Internal seminar; affiliation not listed'
    return f'''<tr data-seminar-date="{e(event['date'])}" data-topic-kind="{e(event['topic_kind'])}">
<td><a href="{e(event['url'])}" title="Original seminar announcement"><time datetime="{e(event['date'])}">{day.strftime('%b %d, %Y')}</time></a><span class="seminar-time">{e(event['time'])} ET</span></td>
<td><strong>{e(event['speaker'])}</strong><span class="seminar-affiliation">{e(affiliation)}</span></td>
<td>{topic_html}</td>
</tr>'''

def table(events, today, body_attribute, caption):
    rows = '\n'.join(render_row(ev, today) for ev in events)
    return f'''<div class="seminar-table-wrap"><table class="seminar-table">
<caption class="sr-only">{e(caption)}</caption>
<thead><tr><th scope="col">date</th><th scope="col">speaker</th><th scope="col">topic / reading</th></tr></thead>
<tbody {body_attribute}>{rows}</tbody>
</table></div>'''

def render(data, today):
    events = data['events']
    upcoming = sorted((ev for ev in events if ev['date'] >= today.isoformat()), key=lambda ev:ev['date'])
    past = sorted((ev for ev in events if ev['date'] < today.isoformat()), key=lambda ev:ev['date'], reverse=True)
    years = sorted({ev['date'][:4] for ev in past}, reverse=True)
    groups=[]
    for i, year in enumerate(years):
        entries=[ev for ev in past if ev['date'].startswith(year)]
        opened=' open' if i==0 else ''
        groups.append(f'''<details class="seminar-year" data-seminar-year="{year}"{opened}>
<summary><span class="seminar-year-label">{year}</span><span class="seminar-year-count">{len(entries)} seminars</span></summary>
{table(entries,today,'data-past-seminars',f'{year} past seminars')}
</details>''')
    return f'''{START}
<div class="wrap" id="seminar-programme">
<header class="page-head">
<h1>seminars</h1>
<p class="lead">Conversations on genome structure, population genetics, and evolution.</p>
</header>
<div class="seminar-intro">
<p>Charikleia (Clio) Karageorgiou organizes the Gokcumen Lab / BEAGL seminar series at the University at Buffalo. This page brings together its past seminars and announced upcoming events. Seminars at MOSAIC in Aarhus will be added as they are announced.</p>
<p class="note">Dates link to the original announcements. Start times are shown in Eastern Time (Buffalo). Suggested reading is labeled separately from a formal talk title.</p>
</div>
<div class="seminar-search" hidden>
<label for="seminar-search">Find a seminar</label>
<input type="search" id="seminar-search" placeholder="Speaker, institution, topic, or year" autocomplete="off">
<p class="note" id="seminar-result-count" role="status">{len(events)} seminars</p>
</div>
<section class="seminar-section" id="upcoming" aria-labelledby="upcoming-title">
<h2 id="upcoming-title">upcoming <span class="seminar-section-count" data-upcoming-count>{len(upcoming)}</span></h2>
{table(upcoming,today,'data-upcoming-seminars','Upcoming seminars organized for the Gokcumen Lab / BEAGL series')}
<p class="note" data-upcoming-empty{' hidden' if upcoming else ''}>No upcoming seminars listed.</p>
</section>
<section class="seminar-section" id="past" aria-labelledby="past-title">
<h2 id="past-title">past seminars <span class="seminar-section-count" data-past-count>{len(past)}</span></h2>
<div data-past-years>{''.join(groups)}</div>
</section>
<p class="note" data-seminar-no-results hidden>No seminars match your search.</p>
<p class="note seminar-source">Programme checked on November 9, 2026. <a href="{e(data['source'])}">Original Gokcumen Lab calendar ↗</a></p>
</div>
{END}'''

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--as-of',type=date.fromisoformat)
    args=parser.parse_args()
    data=json.loads((ROOT/'data/seminars.json').read_text())
    today=args.as_of or datetime.now(ZoneInfo(data['timezone'])).date()
    assert len({(ev['date'],ev['speaker']) for ev in data['events']})==len(data['events']), 'Duplicate seminar'
    path=ROOT/'seminars.html'
    if path.exists():
        template=path.read_text()
    else:
        template=(ROOT/'index.html').read_text()
        head,rest=template.split('</head>',1)
        head=re.sub(r'<title>.*?</title>','<title>Seminars | MOSAIC Lab</title>',head)
        head=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*(")',r'\g<1>Past and upcoming evolutionary genomics seminars organized by Clio Karageorgiou, with speakers, dates, and reading.\2',head)
        head=re.sub(r'(<meta property="og:title" content=")[^"]*(")',r'\g<1>Seminars | MOSAIC Lab\2',head)
        head=head.replace('href="https://mosaic-lab-aarhus.github.io/"','href="https://mosaic-lab-aarhus.github.io/seminars.html"').replace('content="https://mosaic-lab-aarhus.github.io/"','content="https://mosaic-lab-aarhus.github.io/seminars.html"')
        rest=rest.replace(' aria-current="page"','').replace('<a href="seminars.html">','<a href="seminars.html" aria-current="page">')
        template=head+'</head>'+rest
        template=re.sub(r'(<main id="main">).*?(</main>)',lambda m:m.group(1)+'\n'+START+'\n'+END+'\n'+m.group(2),template,flags=re.S)
    assert START in template and END in template
    template=re.sub(re.escape(START)+'.*?'+re.escape(END),lambda _:render(data,today),template,flags=re.S)
    path.write_text(template)
    print(f'Rendered {len(data["events"])} seminars as of {today}')

if __name__=='__main__':
    main()
