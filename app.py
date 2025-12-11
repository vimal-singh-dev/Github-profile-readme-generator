import streamlit as st
from io import BytesIO
import qrcode
import base64
import json
import requests
from datetime import datetime
import uuid
# Lottie optional - will only be used if installed
try:
    from streamlit_lottie import st_lottie
except Exception:
    st_lottie = None

PRESETS_FILE = "presets.json"

# -------------------- Helpers --------------------
def load_presets():
    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_presets(presets):
    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2, ensure_ascii=False)

def badge_md(name):
    from urllib.parse import quote_plus
    safe = quote_plus(name)
    return f"![{name}](https://img.shields.io/badge/{safe}-informational?style=for-the-badge&logo={safe}&logoColor=white)"

def make_qr_png(url, box_size=10, border=2):
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def download_bytes_button(data_bytes, filename, label):
    b64 = base64.b64encode(data_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

def load_lottie_url(url):
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def generate_markdown(data, template="clean-minimal", include_qr=False, qr_filename=None):
    lines = []
    name = data.get("name","Your Name")
    title = data.get("title","")
    about = data.get("about","")
    socials = data.get("socials",[])
    tech = data.get("tech",[])
    education = data.get("education","")
    cpi = data.get("cpi","")
    certs = data.get("certifications",[])
    projects = data.get("projects",[])
    objective = data.get("objective","")
    phone = data.get("phone","")
    email = data.get("email","")
    linkedin = data.get("linkedin","")
    github = data.get("github","")

    if template == "clean-minimal":
        lines.append(f"# {name}")
        if title: lines.append(f"**{title}**")
        lines.append("\n---\n")
        if about: lines.append(about + "\n")
        if socials:
            badges = []
            for s in socials:
                label = s.get('label','Link')
                url = s.get('url','')
                if url:
                    badges.append(f"[{label}]({url})")
            if badges:
                lines.append(" | ".join(badges) + "\n")
        if tech:
            lines.append("\n**Tech:**\n")
            lines.append(" ".join([badge_md(t) for t in tech]) + "\n")
        if projects:
            lines.append("\n---\n\n## Projects\n")
            for p in projects:
                lines.append(f"### {p.get('name')}\n")
                if p.get("tags"): lines.append(f"*{p.get('tags')}*  \n")
                if p.get("links"):
                    for l in p.get("links"):
                        if l.strip():
                            lines.append(f"[Repo / Link]({l})  \n")
                if p.get("desc"): lines.append(p.get("desc") + "\n")
        lines.append("\n---\n")
        lines.append("Contact:  \n")
        if email: lines.append(f"- Email: {email}")
        if phone: lines.append(f"- Phone: {phone}")
        if github: lines.append(f"- GitHub: {github}")
        return "\n".join(lines)

    if template == "fancy-animated":
        lines.append(f"# 👋 Hi, I'm **{name}**")
        if title: lines.append(f"### {title}")
        lines.append("\n---\n")
        if about: lines.append(about + "\n")
        # social badges
        social_badges = []
        for s in socials:
            label = s.get('label','Link').lower()
            url = s.get('url','')
            if url:
                if 'instagram' in label:
                    social_badges.append(f"[![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?logo=Instagram&logoColor=white)]({url})")
                elif 'linkedin' in label:
                    social_badges.append(f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)]({url})")
                elif 'email' in label:
                    social_badges.append(f"[![email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:{url})")
                else:
                    social_badges.append(f"[{s.get('label')}]({url})")
        if social_badges:
            lines.append(" ".join(social_badges) + "\n")

        gh = (github or "").strip().rstrip("/").split("/")[-1] if github else ""
        if gh:
            lines.append("\n---\n\n## 📊 GitHub Highlights\n")
            lines.append(f"![](https://github-readme-stats.vercel.app/api?username={gh}&show_icons=true&theme=radical&count_private=true)\n")
            lines.append(f"![](https://github-readme-stats.vercel.app/api/top-langs/?username={gh}&layout=compact&theme=radical)\n")
            lines.append(f"![](https://github-readme-streak-stats.herokuapp.com/?user={gh}&theme=radical)\n")

        if tech:
            lines.append("\n---\n\n# 💻 Tech Stack\n")
            lines.append(" ".join([badge_md(t) for t in tech]) + "\n")

        if projects:
            lines.append("\n---\n\n# 🚀 Selected Projects\n")
            for p in projects:
                lines.append(f"### 🔹 {p.get('name')}  \n")
                if p.get("tags"): lines.append(f"**Category:** {p.get('tags')}  \n")
                if p.get("links"):
                    for l in p.get("links"):
                        if l.strip():
                            lines.append(f"[Link]({l})  \n")
                if p.get("desc"): lines.append(p.get("desc") + "  \n")
                lines.append("\n")
        if include_qr and qr_filename:
            lines.append("\n---\n")
            lines.append(f"## 🔗 Portfolio QR  \n![]({qr_filename})  \n")
        lines.append("\n---\n")
        lines.append("Contact & Links  \n")
        if email: lines.append(f"- Email: {email}  ")
        if linkedin: lines.append(f"- LinkedIn: {linkedin}  ")
        if github: lines.append(f"- GitHub: {github}  ")
        return "\n".join(lines)

    if template == "resume-style":
        lines.append(f"# {name} \n**{title}**\n")
        lines.append("---\n")
        if about: lines.append(f"**Profile:** {about}\n")
        if tech:
            lines.append("\n**Skills:**\n")
            lines.append(", ".join(tech) + "\n")
        if education:
            lines.append("\n**Education:**\n")
            lines.append(f"- {education} (CPI: {cpi})\n")
        if certs:
            lines.append("\n**Certifications:**\n")
            for c in certs:
                lines.append(f"- {c}\n")
        if projects:
            lines.append("\n**Projects:**\n")
            for p in projects:
                links_str = ", ".join([l for l in p.get('links',[]) if l.strip()])
                lines.append(f"- **{p.get('name')}** — {p.get('desc')} ({links_str})\n")
        lines.append("\n**Contact:**\n")
        if email: lines.append(f"- Email: {email}\n")
        if phone: lines.append(f"- Phone: {phone}\n")
        if linkedin: lines.append(f"- LinkedIn: {linkedin}\n")
        if github: lines.append(f"- GitHub: {github}\n")
        return "\n".join(lines)

    return "\n".join(lines)

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title='README Maker Final', layout='wide', initial_sidebar_state='expanded')

# Themed animated header CSS
dark_mode = st.sidebar.checkbox('Dark Mode', value=True)
if dark_mode:
    st.markdown(
        """
        <style>
        .animated-header {
            font-size:34px;
            font-weight:700;
            background: linear-gradient(90deg,#7f5af0,#00d4ff,#7f5af0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: slideBG 4s linear infinite;
        }
        @keyframes slideBG { 0% {background-position:0%} 100% {background-position:100%} }
        .card { background: #0f1724; padding:12px; border-radius:12px; box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        .muted { color: #9aa4b2; }
        </style>
        """, unsafe_allow_html=True)
else:
    st.markdown(
        """
        <style>
        .animated-header {
            font-size:34px;
            font-weight:700;
            background: linear-gradient(90deg,#ff7b7b,#ffd36b,#7bf7c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: slideBG 5s linear infinite;
        }
        @keyframes slideBG { 0% {background-position:0%} 100% {background-position:100%} }
        .card { background: #ffffff; padding:12px; border-radius:12px; box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
        .muted { color: #6b7280; }
        </style>
        """, unsafe_allow_html=True)

st.markdown('<div class="animated-header">📄 README Maker — Interactive & Animated</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Add multiple projects, URLs, socials; save presets; import from GitHub; download README & QR.</p>', unsafe_allow_html=True)

# Sidebar: templates, presets, import
with st.sidebar:
    st.header('Options & Presets')
    template = st.selectbox('Template', ['clean-minimal','fancy-animated','resume-style'])
    include_qr = st.checkbox('Generate QR code', value=True)
    st.markdown('---')
    st.subheader('Presets')
    presets = load_presets()
    preset_names = ['<select>'] + list(presets.keys())
    selected_preset = st.selectbox('Load preset', preset_names)
    if st.button('Load preset') and selected_preset != '<select>':
        st.session_state['loaded_preset'] = presets[selected_preset]
        st.rerun()
    st.text_input('Preset name to save', key='preset_name_input')
    if st.button('Save preset'):
        name_key = st.session_state.get('preset_name_input','').strip() or f'preset-{uuid.uuid4().hex[:6]}'
        presets[name_key] = {
            'name': st.session_state.get('form_name', 'Your Name'),
            'title': st.session_state.get('form_title',''),
            'about': st.session_state.get('form_about',''),
            'socials': st.session_state.get('form_socials',[]),
            'tech': st.session_state.get('form_tech',[]),
            'education': st.session_state.get('form_education',''),
            'cpi': st.session_state.get('form_cpi',''),
            'certifications': st.session_state.get('form_certs',[]),
            'projects': st.session_state.get('projects',[]),
            'github': st.session_state.get('form_github',''),
            'phone': st.session_state.get('form_phone',''),
            'email': st.session_state.get('form_email',''),
            'linkedin': st.session_state.get('form_linkedin','')
        }
        save_presets(presets)
        st.success(f'Preset saved as {name_key}')
    if st.button('Delete preset'):
        key = st.session_state.get('preset_name_input','').strip()
        if key and key in presets:
            presets.pop(key)
            save_presets(presets)
            st.success(f'Deleted {key}')
    st.markdown('---')
    st.subheader('GitHub Import')
    gh_username = st.text_input('GitHub username', value='')
    gh_token = st.text_input('GitHub token (optional)', value='', type='password')
    if st.button('Import from GitHub'):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if gh_token:
            headers['Authorization'] = f'token {gh_token}'
        try:
            if not gh_username:
                st.error('Enter a GitHub username to import.')
            else:
                u = requests.get(f'https://api.github.com/users/{gh_username}', headers=headers, timeout=10)
                r = requests.get(f'https://api.github.com/users/{gh_username}/repos?per_page=100&sort=pushed', headers=headers, timeout=10)
                if u.status_code == 200:
                    user = u.json()
                    imported = {
                        'name': user.get('name') or user.get('login') or '',
                        'title': user.get('bio') or '',
                        'about': user.get('bio') or '',
                        'socials': [],
                        'tech': [],
                        'education': '',
                        'cpi': '',
                        'certifications': [],
                        'projects': []
                    }
                    repos = r.json() if r.status_code==200 else []
                    for repo in repos[:8]:
                        imported['projects'].append({
                            'name': repo.get('name'),
                            'links': [repo.get('html_url')],
                            'tags': repo.get('language') or '',
                            'desc': repo.get('description') or ''
                        })
                    st.session_state['loaded_preset'] = imported
                    st.success('Imported GitHub profile & top repos into the form.')
                    st.rerun()
                else:
                    st.error('GitHub import failed — check username or rate limits.')
        except Exception as e:
            st.error(f'Import error: {e}')

# Use loaded preset if present
preset = st.session_state.get('loaded_preset', None)

# Main form layout
col1, col2 = st.columns([2,1])
with col1:
    st.subheader('Profile')
    form_name = st.text_input('Full name', value=(preset or {}).get('name','Your Name'), key='form_name')
    form_title = st.text_input('Title', value=(preset or {}).get('title',''), key='form_title')
    form_about = st.text_area('About', value=(preset or {}).get('about',''), height=140, key='form_about')
    st.markdown('---')
    st.subheader('Contact & Socials')
    # dynamic socials (list of dicts with label,url)
    if 'form_socials' not in st.session_state or st.session_state.get('loaded_preset'):
        st.session_state['form_socials'] = (preset or {}).get('socials', [
            {'label':'LinkedIn','url':''},
            {'label':'Email','url':'your-email@example.com'}
        ])
        st.session_state['loaded_preset'] = None

    st.write('Social links (label + url)')
    for i, s in enumerate(st.session_state['form_socials']):
        cols = st.columns([2,5,1])
        lbl = cols[0].text_input(f'Label {i+1}', value=s.get('label',''), key=f's_label_{i}')
        url = cols[1].text_input(f'URL {i+1}', value=s.get('url',''), key=f's_url_{i}')
        rem = cols[2].button('Remove', key=f's_rem_{i}')
        st.session_state['form_socials'][i] = {'label': lbl, 'url': url}
        if rem:
            st.session_state['form_socials'].pop(i)
            st.rerun()
    if st.button('Add Social'):
        st.session_state['form_socials'].append({'label':'New','url':''})
        st.rerun()

    st.markdown('---')
    st.subheader('Education & Certs')
    form_education = st.text_input('Education', value=(preset or {}).get('education',''), key='form_education')
    form_cpi = st.text_input('CPI / Percentage', value=(preset or {}).get('cpi',''), key='form_cpi')
    form_certs = st.text_area('Certifications (one per line)', value="\\n".join((preset or {}).get('certifications',[])), key='form_certs')

with col2:
    st.subheader('Skills & Projects')
    form_tech_raw = st.text_area('Tech skills (comma-separated)', value=",".join((preset or {}).get('tech', [])), height=150, key='form_tech')

    # Projects management (dynamic)
    if 'projects' not in st.session_state or st.session_state.get('loaded_preset'):
        st.session_state['projects'] = (preset or {}).get('projects', [])
        st.session_state['loaded_preset'] = None

    # Lottie animation for projects sidebar (if available)
    if st_lottie:
        lottie_projects = load_lottie_url('https://assets7.lottiefiles.com/packages/lf20_touohxv0.json')
        if lottie_projects:
            try:
                st_lottie(lottie_projects, height=120, key='lottie_projects_side')
            except Exception:
                pass

    if st.button('Add Project'):
        st.session_state['projects'].append({'name':'New Project','links':[''],'tags':'','desc':''})
        st.rerun()

    # Display projects with ability to add/remove links per project
    remove_indices = []
    for i, proj in enumerate(st.session_state['projects']):
        st.markdown(f'**Project #{i+1}**', unsafe_allow_html=True)
        pcols = st.columns([3,1])
        pname = pcols[0].text_input(f'Name {i}', value=proj.get('name',''), key=f'p_name_{i}')
        prem = pcols[1].button('Remove', key=f'p_rem_{i}')
        if prem:
            remove_indices.append(i)
        # links editor
        links = proj.get('links',[])
        for j, link in enumerate(links):
            lcols = st.columns([8,1])
            linkv = lcols[0].text_input(f'Link {i}.{j}', value=link, key=f'p_{i}_link_{j}')
            lrem = lcols[1].button('x', key=f'p_{i}_linkrem_{j}')
            links[j] = linkv
            if lrem:
                links.pop(j)
                st.rerun()
        if st.button(f'Add link to project {i+1}', key=f'addlink_{i}'):
            links.append('')
            st.rerun()
        ptags = st.text_input(f'Tags {i}', value=proj.get('tags',''), key=f'p_tags_{i}')
        pdesc = st.text_area(f'Description {i}', value=proj.get('desc',''), key=f'p_desc_{i}', height=80)
        # write back
        st.session_state['projects'][i] = {'name':pname, 'links':links, 'tags':ptags, 'desc':pdesc}
    # remove after loop to avoid index shift issues
    if remove_indices:
        for idx in sorted(remove_indices, reverse=True):
            st.session_state['projects'].pop(idx)
        st.rerun()

# Buttons to reorder or clear
pc1, pc2, pc3 = st.columns(3)
if pc1.button('Clear All Projects'):
    st.session_state['projects'] = []
    st.rerun()
if pc2.button('Load Example Projects'):
    st.session_state['projects'] = [
        {'name':'Example Project','links':[''],'tags':'Example','desc':'A sample project entry.'}
    ]
    st.rerun()

# Quick Save Preset
if st.button('Quick Save Preset (auto name)'):
    presets = load_presets()
    key = f'preset-{uuid.uuid4().hex[:6]}'
    presets[key] = {
        'name': st.session_state.get('form_name',''),
        'title': st.session_state.get('form_title',''),
        'about': st.session_state.get('form_about',''),
        'socials': st.session_state.get('form_socials',[]),
        'tech': [t.strip() for t in st.session_state.get('form_tech','').split(',') if t.strip()],
        'education': st.session_state.get('form_education',''),
        'cpi': st.session_state.get('form_cpi',''),
        'certifications': [c.strip() for c in st.session_state.get('form_certs','').splitlines() if c.strip()],
        'projects': st.session_state.get('projects',[]),
        'github': st.session_state.get('form_github',''),
        'phone': st.session_state.get('form_phone',''),
        'email': st.session_state.get('form_email',''),
        'linkedin': st.session_state.get('form_linkedin','')
    }
    save_presets(presets)
    st.success(f'Saved preset {key}')

# Assemble final data
data = {
    'name': st.session_state.get('form_name','Your Name'),
    'title': st.session_state.get('form_title',''),
    'about': st.session_state.get('form_about',''),
    'socials': st.session_state.get('form_socials',[]),
    'tech': [t.strip() for t in st.session_state.get('form_tech','').split(',') if t.strip()],
    'education': st.session_state.get('form_education',''),
    'cpi': st.session_state.get('form_cpi',''),
    'certifications': [c.strip() for c in st.session_state.get('form_certs','').splitlines() if c.strip()],
    'projects': st.session_state.get('projects',[]),
    'objective': 'I am looking for internships or entry-level roles to build and learn.',
    'phone': st.session_state.get('form_phone',''),
    'email': st.session_state.get('form_email',''),
    'linkedin': st.session_state.get('form_linkedin',''),
    'github': st.session_state.get('form_github','')
}

# Lottie header (small, only if available)
if st_lottie:
    lottie_header = load_lottie_url('https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json')
    if lottie_header:
        try:
            st_lottie(lottie_header, height=140, key='lottie_header_main')
        except Exception:
            pass

# QR generation and preview
qr_filename = None
if include_qr:
    qr_url = st.text_input('Portfolio / Profile URL (for QR)', value=data.get('github') or '')
    if qr_url:
        qr_buf = make_qr_png(qr_url)
        qr_filename = 'portfolio-qr.png'
        st.image(qr_buf, caption='Generated QR', width=160)
        download_bytes_button(qr_buf.getvalue(), qr_filename, 'Download QR PNG')

# Generate markdown
md = generate_markdown(data, template=template, include_qr=bool(qr_filename), qr_filename=qr_filename)

st.markdown('---')
st.subheader('Preview / Generated README.md')
st.code(md, language='markdown')

# Download options
dlc1, dlc2 = st.columns(2)
with dlc1:
    if st.button('Download README.md'):
        st.download_button('Click to download', md.encode('utf-8'), file_name='README.md', mime='text/markdown')
with dlc2:
    if st.button('Copy to clipboard (open preview, select & copy)'):
        st.info('Use the download button or copy directly from the preview.')

st.markdown('\\n\\n---\\nBuilt with ❤️ — README Maker Final (Clean)')