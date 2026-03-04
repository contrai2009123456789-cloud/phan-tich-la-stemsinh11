import os
from flask import Flask, request, render_template, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# du lei chat
thongtin_chat = {
    'Nitrogen (N)': {
        'trieu_chung': 'Cây bị còi cọc, chóp lá hóa vàng',
        'goi_y_bosung': 'Bổ sung phân đạm (ure, ammonium sulfate)'
    },
    'Phosphorus (P)': {
        'trieu_chung': 'Lá nhỏ, màu lục đậm; thân, rễ kém phát triển',
        'goi_y_bosung': 'Bổ sung phân lân (super lân, lân nung chảy)'
    },
    'Potassium (K)': {
        'trieu_chung': 'Lá màu vàng nhạt, mép lá màu đỏ',
        'goi_y_bosung': 'Bổ sung phân kali (KCl, K2SO4)'
    },
    'Magnesium (Mg)': {
        'trieu_chung': 'Lá màu vàng; mép phiến lá màu cam, đỏ',
        'goi_y_bosung': 'Bổ sung MgSO4 hoặc vôi dolomite'
    },
    'Iron (Fe)': {
        'trieu_chung': 'Gân lá xanh, phiến lá vàng',
        'goi_y_bosung': 'Bổ sung chelate sắt hoặc FeSO4'
    },
    'Manganese (Mn)': {
        'trieu_chung': 'Lá có vết lớn đốm hoại tử dọc theo gân lá',
        'goi_y_bosung': 'Bổ sung MnSO4'
    },
    'Boron (B)': {
        'trieu_chung': 'Vết đốm đen ở lá non và đỉnh sinh trưởng',
        'goi_y_bosung': 'Bổ sung Borax hoặc axit boric'
    },
    'Zinc (Zn)': {
        'trieu_chung': 'Lá có vết hoại tử',
        'goi_y_bosung': 'Bổ sung ZnSO4'
    },
    'Copper (Cu)': {
        'trieu_chung': 'Lá non màu lục đậm',
        'goi_y_bosung': 'Bổ sung CuSO4'
    },
    'Molybdenum (Mo)': {
        'trieu_chung': 'Cây còi cọc, lá màu lục nhạt',
        'goi_y_bosung': 'Bổ sung ammonium molybdate'
    },
    'Sulfur (S)': {
        'trieu_chung': 'Lá hóa vàng, rễ kém phát triển',
        'goi_y_bosung': 'Bổ sung phân chứa lưu huỳnh'
    },
    'Calcium (Ca)': {
        'trieu_chung': 'Lá nhỏ, mềm; chồi đỉnh bị chết',
        'goi_y_bosung': 'Bổ sung vôi hoặc Ca(NO3)2'
    },
    'Chlorine (Cl)': {
        'trieu_chung': 'Lá nhỏ và hóa vàng',
        'goi_y_bosung': 'Bổ sung phân có clo (KCl)'
    }
}

# dacnh sach trieu chung ung voiw thieu chat gi
trieuchung_to_chat = {
    'Cây còi cọc, chóp lá vàng': ['Nitrogen (N)'],
    'Lá nhỏ, màu lục đậm': ['Phosphorus (P)'],
    'Thân, rễ kém phát triển': ['Phosphorus (P)', 'Sulfur (S)'],
    'Lá màu vàng nhạt, mép lá đỏ': ['Potassium (K)'],
    'Lá vàng, mép lá cam/đỏ': ['Magnesium (Mg)'],
    'Gân lá xanh, phiến lá vàng': ['Iron (Fe)'],
    'Lá nhỏ và vàng': ['Chlorine (Cl)'],
    'Đốm hoại tử dọc gân lá': ['Manganese (Mn)'],
    'Lá non màu lục đậm': ['Copper (Cu)'],
    'Đốm hoại tử trên lá': ['Zinc (Zn)'],
    'Cây còi cọc, lá lục nhạt': ['Molybdenum (Mo)'],
    'Đốm đen ở lá non, chồi chết': ['Boron (B)'],
    'Lá vàng, rễ kém': ['Sulfur (S)'],
    'Lá nhỏ mềm, chồi đỉnh chết': ['Calcium (Ca)']
}

@app.route('/', methods=['GET', 'POST'])
def trang_chinh():
    if request.method == 'POST':

        trieuchung_dachon = request.form.getlist('trieuchung')

        if not trieuchung_dachon:
            flash('Vui lòng chọn ít nhất một triệu chứng.')
            return render_template('phantichchu.html',danhsach_trieuchung=trieuchung_to_chat.keys() )

        chat_timduoc = set()
        for trieuchung in trieuchung_dachon:
            if trieuchung in trieuchung_to_chat:
                chat_timduoc.update(trieuchung_to_chat[trieuchung])

        danhsach_chat = list(chat_timduoc)

        if len(danhsach_chat) > 5:
            danhsach_chat = danhsach_chat[:5]

        ketqua = []
        for chat in danhsach_chat:
            thongtin = thongtin_chat.get(chat, {})
            ketqua.append({
                'tenchat': chat,
                'trieuchung': thongtin.get('trieu_chung', ''),
                'goi_y_bosung': thongtin.get('goi_y_bosung', '')
            })

        return render_template(
            'phantichchu.html',
            ketqua=ketqua,
            danhsach_trieuchung=trieuchung_to_chat.keys(),
            trieuchung_dachon=trieuchung_dachon
        )

    return render_template(
        'phantichchu.html',
        danhsach_trieuchung=trieuchung_to_chat.keys()
    )

if __name__ == '__main__':
    app.run()