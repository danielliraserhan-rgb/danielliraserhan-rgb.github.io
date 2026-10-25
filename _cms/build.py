#!/usr/bin/env python3
# Construye las páginas de /predicaciones/ a partir de _cms/predicaciones/*.md
# (los archivos que se editan desde Pages CMS). Uso: python3 _cms/build.py
import re, json, html, glob, os, datetime, yaml
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE=ROOT; SRC=ROOT+'/_cms/predicaciones'; B='https://daniellira.com'
NOW=datetime.date.today().isoformat()
OLD={}
for f in glob.glob(SITE+'/predicaciones/**/index.*',recursive=True): OLD[f]=open(f).read()
def norm_body(b):
    # Tolerar la salida Markdown del editor visual (guiones bajos, escapes, viñetas *)
    b=b.replace('\r\n','\n').replace('\u00a0',' ')
    b=re.sub(r'(?<![\w\\])__(?=\S)(.+?)(?<=\S)__(?!\w)',r'**\1**',b)
    b=re.sub(r'(?<![\w\\_])_(?=\S)(.+?)(?<=\S)_(?![\w_])',r'*\1*',b)
    b=re.sub(r'^(\s*)[*+] ',r'\1- ',b,flags=re.M)
    b=re.sub(r'^(#{2,3}) +\*\*(.+)\*\*\s*$',r'\1 \2',b,flags=re.M)
    b=re.sub(r'\\([\\`_{}\[\]()#+\-.!>|~])',r'\1',b)
    b=re.sub(r'\n{3,}','\n\n',b)
    b=re.sub(r'^&gt; ?','> ',b,flags=re.M)
    return b.strip()
def S(v): return '' if v is None else str(v).strip()
def load(p):
    t=open(p).read()
    _,fm,body=t.split('---\n',2) if t.startswith('---\n') else ('','','')
    d=yaml.safe_load(fm) or {}
    m={'slug':S(d.get('slug')) or os.path.basename(p)[:-3],'title':S(d.get('title')),'description':S(d.get('description')),
       'series':S(d.get('series')),'campus':S(d.get('campus')),'tipo':S(d.get('tipo')) or 'Predicación','authors':'Daniel Lira'}
    for k in ('seo_title','lugar','combina'):
        if S(d.get(k)): m[k]=S(d.get(k))
    if S(d.get('video_start')): m['start']=S(d.get('video_start'))
    m['keywords']=[S(x) for x in (d.get('keywords') or []) if S(x)]
    m['date']=S(d.get('date'))
    vid=re.search(r'(?:v=|youtu\.be/|embed/)([\w-]{11})',S(d.get('video')))
    m['nv']=bool(d.get('manuscript')) or not vid
    m['id']=vid.group(1) if vid else (S(d.get('id')) or m['slug'])
    m['priv']=bool(d.get('video_private'))
    m['yt_title']=S(d.get('video_title')) or m['title']; m['canal']=S(d.get('canal'))
    m['dur']=int(d['video_duration']) if S(d.get('video_duration')).isdigit() else 0
    m['upd']=S(d.get('video_upload_date'))
    m['part']=int(d['part']) if S(d.get('part')).isdigit() else None
    m['pub']=S(d.get('published_month')) or NOW[:7]
    m['published']=d.get('published',True) is not False
    m['orden']=int(d['orden']) if S(d.get('orden')).isdigit() else 10**6
    img=S(d.get('image'))
    m['image']=img
    m['ogi']=(img if img.startswith('http') else B+'/'+img.lstrip('/')) if img else f"{B}/predicaciones/{m['slug']}/og.jpg"
    m['body']=norm_body(body)
    return m
def iso_dur(s): return f"PT{s//3600}H{s%3600//60}M{s%60}S" if s>=3600 else f"PT{s//60}M{s%60}S"
CHURCH='Convivencia Familiar Monterrey'
MES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
def fdate(d):
    if not d: return 'Fecha por confirmar'
    p=d.split('-')
    return f"{MES[int(p[1])-1]} de {p[0]}" if len(p)>=2 else p[0]
def ainote(m,place):
    k={'Predicación':'una predicación','Clase':'una clase'}.get(m['tipo'],'una conversación')
    src='del manuscrito de' if m['nv'] else 'de la transcripción de'
    v='Predicada' if m['nv'] else 'Publicada'
    if not m['date']:
        tail=f"Lugar: {html.escape(place)}." if 'por confirmar' not in place else ''
    else:
        pre=f"{v} en"
        tail=f'{pre} <time datetime="{m["date"]}">{fdate(m["date"])}</time> en {html.escape(place)}' + '.'
    if m['nv']: base=f"Texto completo del manuscrito de Daniel Lira para {k}; solo se añadieron subtítulos y se corrigieron ortografía y puntuación."
    else: base=f"Transcripción completa de {k}, con las palabras de Daniel Lira; solo se añadieron subtítulos, párrafos y puntuación, y se limpiaron muletillas, repeticiones y errores de transcripción."
    if m.get('combina'): base+=f" Este texto combina la versión predicada con el manuscrito de Daniel Lira para el mismo mensaje («{html.escape(m['combina'])}»): lo que solo estaba en el manuscrito se integró con sus propias palabras."
    return f"{base} {tail}".strip()
def vt(s):
    s=re.sub(r'\s+',' ',s).strip()
    s=re.sub(r'(¿[^?¿]*?)-(?=\s|$|\")',r'\1?',s)
    return s.replace('¿Donde','¿Dónde')
def dpar(d): return datetime.date(1900,1,1) if not d else datetime.date.fromisoformat(d if len(d)>7 else d+'-15')
def load_old(p):
    head,body=open(p).read().split('\n---\n',1); m={}
    for l in head.strip().split('\n'):
        k,v=l.split(':',1); m[k.strip()]=v.strip()
    m['keywords']=[x.strip() for x in m['keywords'].split(';')]
    m.setdefault('authors','Daniel Lira'); m.setdefault('tipo','Predicación'); m['body']=body.strip(); r=meta[m['id']]; m['date']=r['fecha']; m['yt_title']=vt(r['titulo']); m['canal']=r['canal']; m['aprox']='aproximada' in r['nota']; m['nv']=m['id'].startswith('sv-'); m['priv']=m['id'] in PRIV
    return m
def slugify(s):
    import unicodedata
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def inline(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
    t=re.sub(r'\*(.+?)\*',r'<em>\1</em>',t)
    t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',t)
    return t
def body_html(b):
    out=[];toc=[];seen=set()
    for blk in b.split('\n\n'):
        blk=blk.strip()
        if not blk: continue
        im=re.fullmatch(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',blk)
        if im:
            out.append(f'<figure class="body-img"><img src="{html.escape(im.group(2))}" alt="{html.escape(im.group(1))}" loading="lazy" decoding="async" style="max-width:100%;height:auto"></figure>'); continue
        if blk.startswith('## ') or blk.startswith('### '):
            lv=3 if blk.startswith('### ') else 2; h=blk[lv+1:]; i=slugify(re.sub(r'[*«»]','',h))[:60] or 'seccion'
            j=i; n=2
            while j in seen: j=f'{i}-{n}'; n+=1
            seen.add(j)
            if lv==2: toc.append((j,h))
            out.append(f'<h{lv} id="{j}">{inline(h)}</h{lv}>')
        elif all(l.startswith('- ') for l in blk.split('\n')):
            out.append('<ul class="body-list">'+''.join(f'<li>{inline(l[2:])}</li>' for l in blk.split('\n'))+'</ul>')
        elif all(l.startswith('>') for l in blk.split('\n')):
            ps=[x for x in re.split(r'\n>\s*\n',blk)]
            out.append('<blockquote>'+''.join(f'<p>{inline(re.sub(r"^> ?","",x,flags=re.M).replace(chr(10)," "))}</p>' for x in ps if x.strip('> \n'))+'</blockquote>')
        else: out.append(f'<p>{inline(blk).replace(chr(10),"<br>")}</p>')
    return '\n'.join(out),toc
def md_body(b): return re.sub(r'\]\(/',f']({B}/',b)
HEADF=open(f'{SITE}/clases/la-imposicion-de-manos/index.html').read()
FONTS=HEADF[HEADF.index('<link rel="preconnect"'):HEADF.index('<script type="application/ld+json">')]
TOP=HEADF[HEADF.index('<div class="strip"'):HEADF.index('<main>')]
TOP=TOP.replace(' aria-current="page"','').replace('<li><a href="/predicaciones/">','<li><a href="/predicaciones/" aria-current="page">')
FOOT=HEADF[HEADF.index('</main>')+7:]
PERSON=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',HEADF).group(1))['@graph'][1]
PERSON=dict(PERSON); PERSON['jobTitle']='Pastor de Jóvenes'; PERSON['worksFor']={'@type':'Church','name':CHURCH,'address':{'@type':'PostalAddress','addressLocality':'Monterrey','addressRegion':'Nuevo León','addressCountry':'MX'}}
def embed(id,title,start=''):
    t=html.escape(title); st=f'?start={start}' if start else ''
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{id}{st}" title="{t}" loading="lazy" '
     f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')
def video(id,title,start=''):
    t=html.escape(title)
    st=f'&amp;t={start}s' if start else ''
    ds=f' data-start="{start}"' if start else ''
    return (f'<div class="video"><a class="yt-lite" href="https://www.youtube.com/watch?v={id}{st}" data-id="{id}"{ds} aria-label="Reproducir video: {t}">'
     f'<img src="https://i.ytimg.com/vi/{id}/hqdefault.jpg" alt="Miniatura del video {t}" width="480" height="360" loading="lazy" decoding="async">'
     f'<img class="yt-mark" src="/marca/monograma-dl.svg" alt="" width="72" height="72" aria-hidden="true"><span class="yt-play" aria-hidden="true">Reproducir</span></a></div>')
YTJS="<script>document.querySelectorAll('.yt-lite').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+this.dataset.id+'?autoplay=1'+(this.dataset.start?'&start='+this.dataset.start:'');f.title=this.getAttribute('aria-label').replace('Reproducir video: ','');f.allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';f.allowFullscreen=true;this.replaceWith(f);});});</script>"
def head(title,desc,url,typ,ld,extra='',ogi='https://daniellira.com/og-image.jpg',pub=''):
    e=html.escape
    return f'''<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{extra.replace('<!--NODATE-->','')}<link rel="describedby" href="/llms.txt" type="text/markdown">
<meta name="author" content="Daniel Lira Serhan">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#F3EDE2">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/favicon.png">
<meta property="og:type" content="{typ}">
<meta property="og:site_name" content="Daniel Lira">
<meta property="og:locale" content="es_MX">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{ogi}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Daniel Lira: Entender el evangelio desde Génesis">
'''+ (f'<meta property="article:author" content="https://daniellira.com/">\n'+(f'<meta property="article:published_time" content="{pub}">\n' if 'NODATE' not in extra else '')+f'<meta property="article:section" content="Predicaciones">\n' if typ=='article' else '') + f'''<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@Danielliraa11">
<meta name="twitter:creator" content="@Danielliraa11">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{ogi}">
{FONTS}<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False,separators=(',',':'))}</script>
</head>
<body class="s-clases">
{TOP}<main>
'''
PARTN=lambda m:m['part'] or 0
arts=sorted(sorted([m for m in (load(p) for p in sorted(glob.glob(SRC+'/*.md'))) if m['published']],key=lambda m:m['orden']),key=lambda m:(m['date'],-PARTN(m)),reverse=True)
for i,m in enumerate(arts):
    url=f"{B}/predicaciones/{m['slug']}/"; title=m.get('seo_title') or m['title']
    if len(title+' | Daniel Lira')<=60: title+=' | Daniel Lira'
    bh,toc=body_html(m['body']); wc=len(re.findall(r'\w+',m['body']))
    rel=[a for a in arts if a is not m]
    # related: same series first, then nearest by date
    ser=m['series'].split('·')[0].strip()
    rel=sorted(rel,key=lambda a:(a['series'].split('·')[0].strip()!=ser, abs((dpar(a['date'])-dpar(m['date'])).days)))[:3]
    yt=f"https://www.youtube.com/watch?v={m['id']}"
    ld={"@context":"https://schema.org","@graph":[
     {"@type":"Article","@id":url+"#article","headline":m['title'],"description":m['description'],"inLanguage":"es-MX","url":url,"mainEntityOfPage":{"@id":url},**({"datePublished":m["pub"],"dateModified":m["pub"]} if m['date'] else {}),**({"dateCreated":m['date']} if m['date'] else {}),
      "author":[{"@type":"Person","@id":B+"/#daniel","name":"Daniel Lira Serhan","url":B+"/","jobTitle":PERSON['jobTitle'],"worksFor":PERSON['worksFor'],"sameAs":PERSON['sameAs']}],"genre":m['tipo'],"publisher":{"@id":B+"/#daniel"},"image":m["ogi"],
      "isPartOf":[{"@id":B+"/#website"},{"@type":"CollectionPage","@id":B+"/predicaciones/","name":"Predicaciones"}],"articleSection":"Predicaciones","keywords":m['keywords'],"wordCount":wc,
      **({"isBasedOn":{"@type":"VideoObject","@id":url+"#video","name":re.sub(r'\s+',' ',m['yt_title']),"url":yt,"embedUrl":f"https://www.youtube-nocookie.com/embed/{m['id']}","thumbnailUrl":f"https://i.ytimg.com/vi/{m['id']}/hqdefault.jpg",**({"uploadDate":m["upd"] or m["date"]} if (m["upd"] or m["date"]) else {}),**({"duration":iso_dur(m['dur'])} if m['dur'] else {}),"description":m['description'],"inLanguage":"es-MX","publisher":({"@type":"Person","name":"Daniel Lira","url":"https://www.youtube.com/@danielliraserhan"} if "danielliraserhan" in m["canal"] else {"@type":"Organization","name":"Convivencia Familiar Monterrey","url":"https://www.youtube.com/@ConvivenciaMty"})}} if not (m['nv'] or m['priv']) else {}),
      **({} if (m.get('lugar') and 'Convivencia' not in m['lugar']) else {"contentLocation":{"@type":"Church","name":(m['lugar'] if m.get('lugar') else (f"{CHURCH} · {m['campus']}" if m['campus'] else CHURCH)),"address":{"@type":"PostalAddress","addressLocality":"Monterrey","addressRegion":"Nuevo León","addressCountry":"MX"}}}),
      "creditText":"Texto completo de Daniel Lira; edición limitada a subtítulos, párrafos, puntuación, limpieza de muletillas y corrección de errores de transcripción.","isAccessibleForFree":True},
     PERSON,
     {"@type":"WebPage","@id":url,"url":url,"name":title,"inLanguage":"es-MX","relatedLink":[f"{B}/predicaciones/{a['slug']}/" for a in rel],"isPartOf":{"@id":B+"/#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
     {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Inicio","item":B+"/"},{"@type":"ListItem","position":2,"name":"Predicaciones","item":B+"/predicaciones/"},{"@type":"ListItem","position":3,"name":m['title'],"item":url}],"@id":url+"#breadcrumb"},
     {"@type":"WebSite","@id":B+"/#website","url":B+"/","name":"Daniel Lira"}]}
    place=m['lugar'] if m.get('lugar') else ((m['campus'] or 'Estudio 12:2') if 'danielliraserhan' in m['canal'] else f"{CHURCH}" + (f" · {m['campus']}" if m['campus'] else ''))
    e=html.escape
    toch=''.join(f'<li><a href="#{i}">{inline(h)}</a></li>' for i,h in toc)
    relh=''.join(f'<li><a href="/predicaciones/{a["slug"]}/">{e(a["title"])}</a></li>' for a in rel)
    REAL={'Cartas de Pablo desde la cárcel','¿Cómo hacer discípulos?','Efesios (Estudio 12:2)','Ecos de la cruz','Vértice 2023'}
    inser=lambda a:ser in REAL and a['series'].split('·')[0].strip()==ser and not (ser.startswith('Efesios') and a['nv'])
    SR=[a for a in arts if inser(a)] if inser(m) else []
    if len(SR)>1:
        SR=sorted(SR,key=lambda a:(a['part'] or 99, a['date']))
        pos=SR.index(m); prev=SR[pos-1] if pos>0 else None; nxt=SR[pos+1] if pos+1<len(SR) else None
    else: prev=nxt=None
    pn=[]
    if prev: pn.append(f'<a href="/predicaciones/{prev["slug"]}/" rel="prev">← Anterior: {e(prev["title"])}</a>')
    if nxt: pn.append(f'<a href="/predicaciones/{nxt["slug"]}/" rel="next">Siguiente: {e(nxt["title"])} →</a>')
    if m['nv']: cite='Este mensaje no tiene video publicado; el texto es el manuscrito completo de Daniel Lira.'
    elif m['priv']: cite=''
    else: cite=f'Video original: <a href="{yt}" rel="noopener">«{e(m["yt_title"])}»</a>, ' + ('canal de YouTube de Daniel Lira (@danielliraserhan)' if 'danielliraserhan' in m['canal'] else 'canal de YouTube de Convivencia Familiar Monterrey') + '.'
    page=head(title,m['description'],url,'article',ld,f'<link rel="alternate" type="text/markdown" href="/predicaciones/{m["slug"]}/index.md" title="Markdown">\n'+('<!--NODATE-->' if not m['date'] else ''),ogi=m['ogi'],pub=m['pub'])+f'''<section class="post-hero" aria-labelledby="t-post"><div class="wrap">
<p class="eyebrow">Predicaciones · {e(m['tipo']+' · ' if m['tipo']!='Predicación' else '')}{e(m['series']) if m['series'] else e(m['campus'] or CHURCH)}</p>
<h1 id="t-post">{e(m['title'])}</h1>
<p class="byline">{e(m['authors'])}{(' · '+e(place)) if 'por confirmar' not in place else ''}{(f' · <time datetime="{m["date"]}">{fdate(m["date"])}</time>') if m['date'] else ''}</p>
</div></section>
<nav class="wrap crumbs" aria-label="Breadcrumb"><a href="/">Inicio</a> › <a href="/predicaciones/">Predicaciones</a> › {e(m['title'])}</nav>
<article class="article" aria-labelledby="t-post">
<p class="ai-note">{ainote(m,place)}</p>
{'' if (m['nv'] or m['priv']) else embed(m['id'],re.sub(r'\s+',' ',m['yt_title']),m.get('start',''))}
<nav class="toc" aria-label="Contenido"><span class="meta">Contenido</span><ol>{toch}</ol></nav>
{bh}
<p class="cite">Las citas bíblicas se reproducen como se {'escribieron en el manuscrito' if m['nv'] else ('leyeron en la clase' if m['tipo']=='Clase' else 'leyeron en la predicación')}. {cite}</p>

{(f'<nav class="series-nav" aria-label="Serie {e(ser)}"><p class="related"><strong>Serie: {e(ser)}</strong> · parte {SR.index(m)+1} de {len(SR)}</p><p class="related">'+' · '.join(pn)+'</p></nav>') if pn else ''}
<nav class="series-nav related-cross" aria-label="Relacionados"><p class="related"><strong>Relacionados</strong></p><ul>{relh}</ul></nav>
<aside class="author-bio" aria-labelledby="bio-clase"><h2 id="bio-clase">Sobre el autor</h2><p><strong>Daniel Lira Serhan</strong> es maestro de la Biblia en Monterrey, México, y autor de <em>Orígenes: El evangelio desde Génesis</em>. Cursa la MDiv en Talbot School of Theology (Biola University) y estudió en Dallas Baptist University. Es pastor de jóvenes en Convivencia Familiar Monterrey desde 2024 y dirige <a href="https://intensivoconvivencia.com" rel="noopener">Intensivo Convivencia</a>, un programa de discipulado para jóvenes.</p></aside>
<p class="back"><a class="btn" href="/predicaciones/">← Más predicaciones</a> <a class="btn" href="/clases/">Clases adaptadas</a></p>
</article>
</main>
{FOOT}'''
    d=f"{SITE}/predicaciones/{m['slug']}"; os.makedirs(d,exist_ok=True); open(d+'/index.html','w').write(page)
    md=f"""# {m['title']}

*{re.sub('<[^>]+>','',ainote(m,place))}*

- Autor: {m['authors']}
- Tipo: {m['tipo']}
{(f"- Fecha: {fdate(m['date'])}, {place}\n") if m['date'] else (f"- Lugar: {place}\n" if 'por confirmar' not in place else '')}- Video: {'sin video publicado' if m['nv'] else ('sin video publicado' if m['priv'] else yt)}
- URL: {url}
- Idioma: es-MX

---

""" + "" + md_body(m['body']) + "\n"
    open(d+'/index.md','w').write(md); m['md']=md
# index page
url=B+'/predicaciones/'; title='Predicaciones | Daniel Lira'
desc='Predicaciones y clases de Daniel Lira, pastor de jóvenes en Convivencia Familiar Monterrey: el texto completo de cada mensaje, con video cuando está publicado.'
ld={"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","@id":url,"url":url,"name":title,"description":desc,"inLanguage":"es-MX","isPartOf":{"@id":B+"/#website"},"author":{"@id":B+"/#daniel"},
 "mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{B}/predicaciones/{a['slug']}/","name":a['title']} for i,a in enumerate(arts)]},"breadcrumb":{"@id":url+"#breadcrumb"}},
 {"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Inicio","item":B+"/"},{"@type":"ListItem","position":2,"name":"Predicaciones","item":url}]},
 PERSON,{"@type":"WebSite","@id":B+"/#website","url":B+"/","name":"Daniel Lira"}]}
cards=[]
for a in arts:
    e=html.escape; place=CHURCH.replace(' Monterrey','')+(f" · {a['campus']}" if a['campus'] else '')
    cards.append(f'''<article class="card"><div class="meta">{(f'<time datetime="{a["date"]}">{fdate(a["date"])}</time><br>') if a['date'] else ''}{e(a['lugar'] if (a.get('lugar') and 'por confirmar' not in a['lugar']) else (a['campus'] or ('Estudio 12:2' if ('danielliraserhan' in a['canal'] or 'Estudio 12:2' in a['series']) else ('' if a['nv'] else 'Convivencia Familiar'))))}{'<br>'+e(a['tipo']) if a['tipo']!='Predicación' else ''}</div><h3>{e(a['title'])}</h3>{'' if (a['nv'] or a['priv']) else video(a['id'],a['yt_title'],a.get('start',''))}<p class="card-links"><a class="read" href="/predicaciones/{a['slug']}/">Leer</a>{'' if (a['nv'] or a['priv']) else f'<a class="read" href="https://www.youtube.com/watch?v={a["id"]}" rel="noopener">YouTube</a>'}</p></article>''')
cards=[c.replace('<br><br>','<br>').replace('<br></div>','</div>').replace('<div class="meta"><br>','<div class="meta">') for c in cards]
page=head(title,desc,url,'website',ld)+f'''<section class="hero list-hero" aria-labelledby="t-list"><div class="wrap">
<p class="eyebrow">Mensajes y clases</p>
<h1 id="t-list">Predicaciones</h1>
<p>Predicaciones y clases de Daniel Lira, pastor de jóvenes en Convivencia Familiar Monterrey. Cada artículo es el texto completo del mensaje, con sus propias palabras; solo se añadieron subtítulos y puntuación, y se quitaron muletillas y repeticiones. Cuando hay video público o no listado, se incluye.</p>
</div></section>
<nav class="wrap crumbs" aria-label="Breadcrumb"><a href="/">Inicio</a> › Predicaciones</nav>
<section><div class="wrap">
<div class="cards pred">{''.join(cards)}</div>
{YTJS}
</div></section>
</main>
{FOOT}'''
open(f"{SITE}/predicaciones/index.html",'w').write(page)


# ---------- Imágenes OG (solo si cambió el título o falta) ----------
OGT=ROOT+'/_cms/.og-titulos.json'
ogt=json.load(open(OGT)) if os.path.exists(OGT) else {}
from PIL import Image,ImageDraw,ImageFont
import textwrap
FD=ROOT+'/_cms/fonts/'
V,T,P,A=(243,237,226),(31,26,23),(107,98,87),(122,46,30)
for a in arts:
    out=f"{SITE}/predicaciones/{a['slug']}/og.jpg"
    if a['image'] or (ogt.get(a['slug'])==a['title'] and os.path.exists(out)): continue
    mono=ImageFont.truetype(FD+'IBMPlexMono-Medium.ttf',26)
    im=Image.new('RGB',(1200,630),V); d=ImageDraw.Draw(im)
    d.line([(80,70),(1120,70)],fill=T,width=1); d.line([(80,76),(1120,76)],fill=T,width=1)
    d.text((80,100),'DANIEL LIRA · PREDICACIONES',font=mono,fill=A)
    for sz in (76,68,60,52,46):
        f=ImageFont.truetype(FD+'Newsreader-VF.ttf',sz)
        w=max(10,int(1040/(sz*0.48))); lines=textwrap.wrap(a['title'],w)
        if len(lines)*sz*1.12<=360 and all(d.textlength(l,font=f)<=1040 for l in lines): break
    y=170
    for l in lines: d.text((80,y),l,font=f,fill=T); y+=int(sz*1.12)
    d.line([(80,540),(1120,540)],fill=T,width=1)
    d.text((80,560),'daniellira.com',font=mono,fill=P)
    im.save(out,'JPEG',quality=85,optimize=True); ogt[a['slug']]=a['title']
json.dump(ogt,open(OGT,'w'),ensure_ascii=False,indent=0,sort_keys=True)

# ---------- Portada: sección Predicaciones ----------
Hf=SITE+'/index.html'; h=open(Hf).read()
M3=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
items=sorted(sorted(arts,key=lambda m:m['orden']),key=lambda x:x['date'],reverse=True)
def card(x):
    p=x['date'].split('-') if x['date'] else []
    fe=f"{M3[int(p[1])-1]} {p[0]}" if len(p)>=2 else (p[0] if p else '')
    mt=' · '.join(q for q in [x['tipo'],x['series'],fe] if q)
    return f'<article class="card"><div class="meta">{html.escape(mt)}</div><h3>{html.escape(x["title"])}</h3><p class="card-links"><a class="read" href="/predicaciones/{x["slug"]}/">Leer →</a></p></article>'
n=len(arts); lbl=f"{n} predicaci{'ón' if n==1 else 'ones'}"
def homesec(mm):
    s=mm.group(0)
    s=re.sub(r'<div class="cards compact">.*?</div>\n',lambda _:f'<div class="cards compact">{"".join(card(x) for x in items[:3])}</div>\n',s,flags=re.S)
    return re.sub(r'Ver las \d+ predicaciones',f'Ver las {lbl}',s)
h=re.sub(r'<!--PRED-HOME-->.*?<!--/PRED-HOME-->',homesec,h,flags=re.S)
h=re.sub(r'(<span class="mono m c-olivo" data-pred>)[^<]*',lambda mm:mm.group(1)+lbl,h)
open(Hf,'w').write(h)

# ---------- sitemap (lastmod solo cambia si la página cambió) ----------
def changed(f): return OLD.get(f)!=open(f).read()
sm=open(SITE+'/sitemap.xml').read()
prev={u:l for u,l in re.findall(r'<loc>https://daniellira.com/predicaciones/([^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>',sm)}
sm=re.sub(r'<url>\s*<loc>https://daniellira.com/predicaciones/[^<]*</loc>.*?</url>\s*','',sm,flags=re.S)
def lm(u,f): return prev[u] if (u in prev and not changed(f)) else NOW
add=''.join(f'<url>\n  <loc>{B}/predicaciones/{u}</loc>\n  <lastmod>{lm(u,f)}</lastmod>\n</url>\n' for u,f in [('',SITE+'/predicaciones/index.html')]+[(a['slug']+'/',f"{SITE}/predicaciones/{a['slug']}/index.html") for a in arts])
sm=sm.replace('</urlset>',add+'</urlset>'); open(SITE+'/sitemap.xml','w').write(sm)
# ---------- llms.txt / llms-full.txt ----------
L=open(SITE+'/llms.txt').read()
L=re.sub(r'\n## Predicaciones\n.*?(?=\n## |\Z)','',L,flags=re.S)
sec='\n## Predicaciones\n\nPredicaciones y clases de Daniel Lira (pastor de jóvenes en Convivencia Familiar Monterrey). Cada página es el texto completo del mensaje, en sus propias palabras; la edición se limita a subtítulos, párrafos, puntuación y limpieza de muletillas. Incluye el video cuando es público.\n\n'+''.join(f"- [{a['title']}]({B}/predicaciones/{a['slug']}/index.md): {a['description']}"+(f" ({a['date']})" if a['date'] else '')+f" (HTML: {B}/predicaciones/{a['slug']}/)\n" for a in arts)
L=L.replace('\n## Optional',sec+'\n## Optional',1) if '\n## Optional' in L else L.rstrip('\n')+'\n'+sec; open(SITE+'/llms.txt','w').write(L)
F=open(SITE+'/llms-full.txt').read()
F=re.sub(r'\n<!-- PREDICACIONES -->.*\Z','',F,flags=re.S)
F=F.rstrip('\n')+'\n\n<!-- PREDICACIONES -->\n'+''.join(f"\n\n<!-- Fuente: {B}/predicaciones/{a['slug']}/ -->\n\n"+a['md'] for a in arts)
open(SITE+'/llms-full.txt','w').write(F)
# páginas de artículos despublicados/borrados: no se borran automáticamente
print(len(arts),'artículos')
