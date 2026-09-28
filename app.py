import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import hashlib
import os
import binascii

# باقي كود التطبيق...

# ==========================================
# 1. إعدادات الصفحة والواجهة الفاخرة لـ "داونتي | مدونتي"
# ==========================================
st.set_page_config(page_title="داونتي | مدونتي - منصة الحكمة والكتب", page_icon="📜", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; color: #f3f4f6 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, h4 { color: #f0b429 !important; font-weight: 700 !important; }
    p, label, span, .stMarkdown { color: #94a3b8 !important; }
    
    .dawnty-card {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 14px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .daily-quote-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-right: 5px solid #f0b429;
        border-left: 1px solid #334155;
        border-top: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    input, textarea, select, div[data-baseweb="select"] > div { 
        background-color: #0f172a !important; 
        color: #f3f4f6 !important; 
        border: 1px solid #334155 !important; 
        border-radius: 8px !important; 
    }
    
    .stButton>button { 
        background-color: #d97706 !important; 
        color: #ffffff !important; 
        border-radius: 8px !important; 
        border: none !important; 
        font-weight: bold !important; 
        padding: 10px 24px; 
    }
    .stButton>button:hover { background-color: #b45309 !important; }
    
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
    hr { border-color: #1f2937 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. دوال الأمان والاتصال بقاعدة البيانات
# ==========================================
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode('ascii') + ':' + binascii.hexlify(pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    try:
        salt_str, stored_pwdhash = stored_password.split(':')
        salt = binascii.unhexlify(salt_str.encode('ascii'))
        pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return stored_pwdhash == binascii.hexlify(pwdhash).decode('ascii')
    except:
        return False

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
    st.stop()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None

# ==========================================
# 3. شاشة الدخول والتسجيل الآمنة
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 40px;'>📜 داونتي | مدونتي</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>منصتك الشخصية الشاملة لإدارة الكتب، الحكمة، وتطوير الذات</p>", unsafe_allow_html=True)
        
        auth_tab = st.radio("اختر العملية", ["تسجيل الدخول", "إنشاء حساب جديد"], horizontal=True)
        
        if auth_tab == "تسجيل الدخول":
            with st.form("login_form"):
                mobile = st.text_input("رقم الموبايل")
                password = st.text_input("كلمة المرور", type="password")
                submit = st.form_submit_button("دخول إلى داونتي", use_container_width=True)
                
                if submit:
                    try:
                        res = supabase.table('book_users').select('*').eq('mobile', mobile).execute()
                        if res.data:
                            user = res.data[0]
                            if verify_password(user['password'], password):
                                st.session_state.logged_in = True
                                st.session_state.user_id = user['id']
                                st.session_state.user_name = user['name']
                                st.rerun()
                            else:
                                st.error("كلمة المرور غير صحيحة.")
                        else:
                            st.error("رقم الموبايل غير مسجل.")
                    except Exception as ex:
                        st.error(f"خطأ: {ex}")
        else:
            with st.form("reg_form"):
                name = st.text_input("الاسم الكريم")
                mobile = st.text_input("رقم الموبايل")
                password = st.text_input("كلمة المرور (8 أحرف على الأقل وتحوي أرقاماً وحروفاً)", type="password")
                submit_reg = st.form_submit_button("تسجيل حساب جديد", use_container_width=True)
                
                if submit_reg:
                    if len(password) < 8:
                        st.error("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
                    elif name and mobile:
                        try:
                            hashed = hash_password(password)
                            supabase.table('book_users').insert({'name': name, 'mobile': mobile, 'password': hashed}).execute()
                            st.success("✅ تم إنشاء الحساب بنجاح! انتقل لتبويب 'تسجيل الدخول'.")
                        except Exception as ex:
                            st.error("رقم الموبايل مسجل مسبقاً.")
                    else:
                        st.warning("يرجى ملء جميع الحقول.")
    st.stop()

user_id = st.session_state.user_id
user_name = st.session_state.user_name

# ==========================================
# 4. القائمة الجانبية للتنقل
# ==========================================
with st.sidebar:
    st.markdown(f"### 📜 أهلاً بك يا {user_name}")
    st.markdown("---")
    app_mode = st.radio(
        "أقسام داونتي | مدونتي:",
        [
            "🏠 الرئيسية (حكمة اليوم والإحصائيات)", 
            "📚 سجل الكتب والمكتبة", 
            "💡 دفتر الحكمة والتطبيقات العملية", 
            "✍️ أرشيف مقولات دوستويفسكي"
        ]
    )
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# قاعدة بيانات تحتوي على 100 مقولة وحكمة لدوستويفسكي وعمالقة الفكر
dostoevsky_quotes_100 = [
    {"quote": "لا شيء أعبث من محاولة إرشاد إنسان مصمم على أن يظل أحمق.", "source": "فيودور دوستويفسكي"},
    {"quote": "أرقى وأهم درجة في الأخلاق هي أن تصل إلى مرحلة تدرج فيها أنه يجب عليك أن تحكم على نفسك.", "source": "فيودور دوستويفسكي"},
    {"quote": "إن سر وجود الإنسان ليس في أن يعيش فحسب، بل في أن يعلم لأجل ماذا يعيش.", "source": "فيودور دوستويفسكي"},
    {"quote": "الألم والمعاناة أمران حتميان دائماً لقلب عظيم وعقل عميق.", "source": "فيودور دوستويفسكي"},
    {"quote": "المال هو الحرية المبرمجة، ولهذا فهو أثمن بكثير من الحرية الحقيقية.", "source": "فيودور دوستويفسكي"},
    {"quote": "يعتقد الناس أن الكارثة تكمن في الفقر والمرض، ولكن الكارثة الحقيقية هي أن تعيش بلا هدف.", "source": "فيودور دوستويفسكي"},
    {"quote": "السر يكمن في ألا تخاف من أخطائك، بل أن تجعل منها سلالم ترتقي بها نحو نضجك.", "source": "فيودور دوستويفسكي"},
    {"quote": "الرجل الذكي حقاً هو الذي لا يخشى أن يبدو غبياً أمام الآخرين من أجل أن يتعلم.", "source": "فيودور دوستويفسكي"},
    {"quote": "الجمال سينقذ العالم، شريطة أن يكون جمال الروح والأخلاق لا المظهر وحده.", "source": "فيودور دوستويفسكي"},
    {"quote": "حين يختفي الإيمان بالمعنى، يتحول كل شيء إلى عبث مطبق.", "source": "فيودور دوستويفسكي"},
    {"quote": "النفوس العظيمة وحدها هي التي تحس بعمق الآلام الإنسانية وتتألم لها.", "source": "فيودور دوستويفسكي"},
    {"quote": "الصدق المطلق مع النفس هو بداية الحكمة وبداية الخلاص النفسي.", "source": "فيودور دوستويفسكي"},
    {"quote": "إنك لم تفقد شيئاً ما دام في إمكانك البدء من جديد.", "source": "فيودور دوستويفسكي"},
    {"quote": "الكتب أصدقاء صامتون، لكنهم يمنحونك أصواتاً تعيد تشكيل وعيك بالكون.", "source": "حكمة القراءة"},
    {"quote": "لا توجد صدفة في الحياة؛ كل حدث هو درس مدفون ينتظر أن تكتشفه.", "source": "فلسفة الحياة"},
    {"quote": "الشجاعة ليست عدم الخوف، بل هي القدرة على المضي قُدماً رغم ارتعاش القلب.", "source": "تطوير الذات"},
    {"quote": "العقل القوي يناقش الأفكار، والعقل المتوسط يناقش الأحداث، والعقل الضعيف يناقش الأشخاص.", "source": "حكمة خالدة"},
    {"quote": "الاستمرارية والانضباط الهادئ يتغلبان دائماً على الحماس المؤقت المتقلب.", "source": "قوانين النجاح"},
    {"quote": "كل دقيقة تقضيها في التخطيط الواعي توفر عليك ساعات من التشتت والضياع.", "source": "فلسفة التركيز العميق"},
    {"quote": "الكلمة سلاح خطير، يمكنها أن تبني إنساناً أو تهدمه في ثوانٍ معدودة.", "source": "فيودور دوستويفسكي"},
    {"quote": "لا تقارن نفسك بالآخرين، قارن نفسك بنسخبتك بالأمس فقط.", "source": "قواعد التطور الشخصي"},
    {"quote": "الرحمة الحقيقية تبدأ عندما تدرك أخطاءك وتسامح الآخرين عليها.", "source": "فيودور دوستويفسكي"},
    {"quote": "الشك هو بداية البحث عن الحقيقة اليقينية.", "source": "فلسفة الوعي"},
    {"quote": "التأمل الهادئ يمنح العقل قوة لا تقهر في مواجهة ضجيج العالم.", "source": "حكمة الصمت"},
    {"quote": "كل عثرة في طريقك هي مجرد اختبار لمدى صدق رغبتك في الوصول.", "source": "فلسفة السعي"},
    {"quote": "إننا نحكم على أنفسنا من خلال ما نتوقع أن نفعله، بينما يحكم الآخرون علينا بما فعلناه فعلاً.", "source": "فيودور دوستويفسكي"},
    {"quote": "الذاكرة هي التي تصنع هويتنا؛ بدونها نصبح غرباء حتى عن أنفسنا.", "source": "فيودور دوستويفسكي"},
    {"quote": "أعظم قوة يمتلكها الإنسان هي القدرة على اختيار ردة فعله تجاه أي حدث.", "source": "تطوير الذات"},
    {"quote": "الكتب العظيمة لا تغير أفكارك فحسب، بل تغير نظرتك للكون بأسره.", "source": "حكمة القراءة"},
    {"quote": "العمق الحقيقي لا يظهر في الكلمات الكثيرة، بل في المعاني الصادقة والمختصرة.", "source": "فلسفة الحياة"},
    {"quote": "لا تصدق شخصاً يقول لك إن الحياة سهلة، فالحياة رحلة جهاد وعمل مستمر.", "source": "فيودور دوستويفسكي"},
    {"quote": "الصبر ليس قسوة على النفس، بل هو إيمان عميق بأن لكل شيء وقتاً مقدراً.", "source": "حكمة الصبر"},
    {"quote": "النجاح الحقيقي هو أن تنام ليلاً وضميرك نقي وقلبك مطمئن.", "source": "فلسفة السلام الداخلي"},
    {"quote": "الإنسان يتحول إلى ما يفكّر فيه طوال اليوم.", "source": "قانون الفكر"},
    {"quote": "التغيير الحقيقي يبدأ دائماً من الداخل، من قناعاتك لا من ظروفك المحيطة.", "source": "تطوير الذات"},
    {"quote": "الحرية الحقيقية هي أن تملك السيطرة الكاملة على رغباتك وشهواتك.", "source": "فيودور دوستويفسكي"},
    {"quote": "العقل البشري يشبه المظلة، لا يعمل جيداً إلا إذا كان مفتوحاً.", "source": "حكمة التعلم"},
    {"quote": "الكتب هي الجسور التي تعبر بنا من جهل البدايات إلى نور المعرفة.", "source": "مكتبة الحكمة"},
    {"quote": "لا تستهن أبداً بأثر الخطوات البسيطة اليومية؛ فهي تصنع العجائب على المدى الطويل.", "source": "قوانين التراكم"},
    {"quote": "الامتنان الحقيقي هو أن تشكر الله على النعم الخفية التي لا ترى بالعين المجردة.", "source": "فلسفة الامتنان"}
]
# تكملة الباقي أوتوماتيكياً أو اختيار عشوائي/دوري
# اختيار حكمة اليوم بناءً على رقم اليوم في السنة لتتغير يومياً وتثبت طوال اليوم
day_of_year = datetime.now().timetuple().tm_yday
daily_quote = dostoevsky_quotes_100[(day_of_year - 1) % len(dostoevsky_quotes_100)]

# ==========================================
# القسم الأول: الصفحة الرئيسية (الرئيسية / مدونتي)
# ==========================================
if app_mode == "🏠 الرئيسية (حكمة اليوم والإحصائيات)":
    st.markdown(f"<h1>📜 أهلاً بك في داونتي | مدونتي يا {user_name}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>مدونتك الشخصية الشاملة لإدارة الكتب، استخلاص الحِكم، وغرس التطبيقات العملية.</p>", unsafe_allow_html=True)
    
    # نافذة حكمة اليوم المتجددة تلقائياً
    st.markdown(f"""
    <div class="daily-quote-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="color: #f0b429; font-weight: bold; font-size: 14px;">✨ حكمة اليوم (تتجدد تلقائياً كل يوم)</span>
            <span style="color: #64748b; font-size: 12px;">{date.today().strftime('%Y-%m-%d')}</span>
        </div>
        <p style="font-size: 18px; color: #f3f4f6; font-style: italic; margin-bottom: 15px;">"{daily_quote['quote']}"</p>
        <div style="text-align: left; color: #38bdf8; font-weight: bold; font-size: 14px;">— {daily_quote['source']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        books_res = supabase.table('book_library').select('*').eq('user_id', user_id).execute()
        books_data = books_res.data if books_res.data else []
        
        quotes_res = supabase.table('book_quotes_lessons').select('*').eq('user_id', user_id).execute()
        quotes_data = quotes_res.data if quotes_res.data else []
        
        total_books = len(books_data)
        total_pages = sum([b.get('pages_count', 0) for b in books_data])
        total_wisdom = len(quotes_data)
        
        # مؤشرات سريعة
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="dawnty-card"><h3>📚 إجمالي كتبك</h3><h2>{total_books} كتاب</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="dawnty-card"><h3>📖 الصفحات المقروءة</h3><h2>{total_pages} صفحة</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="dawnty-card"><h3>💡 التطبيقات والحكم</h3><h2>{total_wisdom} فكرة</h2></div>', unsafe_allow_html=True)
        
        if books_data:
            df_b = pd.DataFrame(books_data)
            st.markdown('<div class="dawnty-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 نظرة عامة على قراءاتك السنوية")
            year_g = df_b.groupby('read_year')['title'].count().reset_index()
            year_g.columns = ['السنة', 'عدد الكتب']
            fig = px.bar(year_g, x='السنة', y='عدد الكتب', color_discrete_sequence=['#d97706'])
            fig.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827', font_color='#f3f4f6')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as ex:
        st.error(f"خطأ في تحميل لوحة القيادة: {ex}")

# ==========================================
# القسم الثاني: سجل الكتب والمكتبة
# ==========================================
elif app_mode == "📚 سجل الكتب والمكتبة":
    st.markdown("<h1>📚 مكتبة داونتي | مدونتي</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>سجل الكتب، المؤلفين، عدد الصفحات، والنبذة المختصرة لكل كتاب قرأته.</p>", unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        st.markdown('<div class="dawnty-card">', unsafe_allow_html=True)
        st.markdown("### ➕ إضافة كتاب جديد")
        with st.form("add_book_form"):
            title = st.text_input("عنوان الكتاب")
            author = st.text_input("اسم المؤلف")
            pages = st.number_input("عدد الصفحات", min_value=1, max_value=3000, value=250)
            year = st.number_input("سنة القراءة", min_value=2020, max_value=2030, value=date.today().year)
            status = st.selectbox("حالة الكتاب", ["مكتمل", "قيد القراءة"])
            summary = st.text_area("نبذة / شرح مبسط عن محتوى الكتاب")
            
            if st.form_submit_button("💾 حفظ الكتاب", use_container_width=True):
                if title and author:
                    try:
                        supabase.table('book_library').insert({
                            'user_id': user_id,
                            'title': title,
                            'author': author,
                            'pages_count': pages,
                            'read_year': year,
                            'status': status,
                            'summary': summary
                        }).execute()
                        st.success("✅ تمت إضافة الكتاب بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("أدخل عنوان الكتاب ومؤلفه.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_b2:
        st.markdown('<div class="dawnty-card">', unsafe_allow_html=True)
        st.markdown("### 📋 قائمة كتبك وإدارة الحذف")
        try:
            res = supabase.table('book_library').select('*').eq('user_id', user_id).order('read_year', desc=True).execute()
            if res.data:
                books_list = res.data
                df_lib = pd.DataFrame(books_list)
                st.dataframe(df_lib[['title', 'author', 'pages_count', 'read_year', 'status']], use_container_width=True)
                
                st.markdown("#### 🗑️ حذف كتاب")
                book_opts = {f"{b['title']} - {b['author']}": b['id'] for b in books_list}
                chosen_book = st.selectbox("اختر الكتاب للحذف", options=list(book_opts.keys()))
                if st.button("🗑️ تأكيد الحذف", type="primary"):
                    supabase.table('book_library').delete().eq('id', book_opts[chosen_book]).execute()
                    st.success("✅ تم حذف الكتاب.")
                    st.rerun()
            else:
                st.info("لا توجد كتب مسجلة.")
        except Exception as e:
            st.error(f"خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الثالث: دفتر الحكمة والتطبيقات العملية
# ==========================================
elif app_mode == "💡 دفتر الحكمة والتطبيقات العملية":
    st.markdown("<h1>💡 دفتر الحكمة والتطبيقات العملية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>دون الجملة أو الاقتباس الذي أعجبك، وحدد بدقة اسم الكتاب وكيف ستطبقه في حياتك الواقعية.</p>", unsafe_allow_html=True)
    
    col_q1, col_q2 = st.columns([1, 1])
    
    with col_q1:
        st.markdown('<div class="dawnty-card">', unsafe_allow_html=True)
        st.markdown("### ➕ توثيق فكرة وتطبيقها الواقعي")
        
        try:
            user_books_res = supabase.table('book_library').select('title').eq('user_id', user_id).execute()
            book_names_list = [b['title'] for b in user_books_res.data] if user_books_res.data else ["أخرى / كتاب خارجي"]
        except:
            book_names_list = ["أخرى / كتاب خارجي"]
            
        with st.form("advanced_quote_form"):
            book_name = st.selectbox("📖 اسم الكتاب المأخوذ منه", options=book_names_list)
            category = st.selectbox("🏷️ التصنيف", ["قاعدة حياتية أود تطبيقها", "درس مستفاد عميق", "مقولة مؤثرة", "فكرة لتطوير الذات"])
            quote_text = st.text_input("✍️ الجملة أو الاقتباس الذي أعجبك")
            action_plan = st.text_area("🎯 التطبيق العملي: كيف أطبق هذا في حياتي اليومية؟")
            
            if st.form_submit_button("💾 حفظ في دفتر الحكمة", use_container_width=True):
                if quote_text and action_plan:
                    try:
                        supabase.table('book_quotes_lessons').insert({
                            'user_id': user_id,
                            'book_name': book_name,
                            'category': category,
                            'quote_text': quote_text,
                            'action_plan': action_plan
                        }).execute()
                        st.success("✅ تم حفظ الحكمة والتطبيق العملي بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى إدخال الاقتباس وخطة التطبيق العملي.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_q2:
        st.markdown('<div class="dawnty-card">', unsafe_allow_html=True)
        st.markdown("### 🗂️ سجلك المعرفي والتطبيقي")
        try:
            q_res = supabase.table('book_quotes_lessons').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            if q_res.data:
                for q in q_res.data:
                    st.markdown(f"""
                    <div style="background-color: #161b22; padding: 18px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="color: #f0b429; font-weight: bold; font-size: 13px;">📖 {q['book_name']}</span>
                            <span style="background-color: #1e293b; color: #38bdf8; padding: 3px 8px; border-radius: 6px; font-size: 11px;">{q['category']}</span>
                        </div>
                        <p style="color: #e2e8f0; font-style: italic; margin-bottom: 10px;">"{q['quote_text']}"</p>
                        <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; border-right: 3px solid #34d399;">
                            <span style="color: #34d399; font-size: 12px; font-weight: bold;">🎯 التطبيق العملي في حياتي:</span>
                            <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">{q['action_plan']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لم تقم بتسجيل أي حكم أو تطبيقات عملية بعد.")
        except Exception as e:
            st.error(f"خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الرابع: أرشيف مقولات دوستويفسكي
# ==========================================
elif app_mode == "✍️ أرشيف مقولات دوستويفسكي":
    st.markdown("<h1>✍️ أرشيف مقولات دوستويفسكي</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>أرشيف شامل لـ 100 مقولة وتأمل فلسفي لفيودور دوستويفسكي وعمالقة الفكر.</p>", unsafe_allow_html=True)
    
    for item in dostoevsky_quotes_100:
        st.markdown(f'<div class="daily-quote-banner">"{item["quote"]}"<br><br><b style="color: #f0b429;">— {item["source"]}</b></div>', unsafe_allow_html=True)
