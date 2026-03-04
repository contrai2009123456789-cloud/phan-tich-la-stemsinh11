import os
import cv2
import numpy as np
from flask import Flask, request, render_template, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nongnghiepthongminh2024'

app.config['THU_MUC_TAI_LEN'] = 'uploads'
app.config['DINH_DANG_CHO_PHEP'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['THU_MUC_TAI_LEN'], exist_ok=True)


def kiemtra_dinhdang(ten_file):
    return '.' in ten_file and ten_file.rsplit('.', 1)[1].lower() in app.config['DINH_DANG_CHO_PHEP']


# ===== TỪ ĐIỂN THÔNG TIN CHẤT =====
thongtin_chat = {
    'Nitrogen (N)': {
        'trieu_chung': 'Lá già vàng đều từ chóp vào, cây còi cọc.',
        'goi_y_bosung': 'Bổ sung phân đạm (Ure, SA).'
    },
    'Phosphorus (P)': {
        'trieu_chung': 'Lá xanh đậm bất thường, đôi khi chuyển sắc tím/đỏ ở mép.',
        'goi_y_bosung': 'Bổ sung Super lân hoặc DAP.'
    },
    'Potassium (K)': {
        'trieu_chung': 'Mép lá bị cháy nâu như bị bỏng, lá già bị trước.',
        'goi_y_bosung': 'Bổ sung Kali Clorua hoặc Kali Sulfate.'
    },
    'Magnesium (Mg)': {
        'trieu_chung': 'Vàng phần thịt lá nhưng gân lá vẫn giữ màu xanh.',
        'goi_y_bosung': 'Bổ sung Magie Sulfate hoặc Dolomite.'
    },
    'Iron (Fe)': {
        'trieu_chung': 'Lá non bị vàng trắng, gân lá xanh rất mảnh.',
        'goi_y_bosung': 'Phun Chelate sắt qua lá.'
    },
    'Zinc (Zn)': {
        'trieu_chung': 'Lá nhỏ, biến dạng, có các đốm hoại tử màu nâu trắng.',
        'goi_y_bosung': 'Bổ sung Kẽm Sulfate.'
    }
}


def phan_tich_la(duongdan_anh):
    anh = cv2.imread(duongdan_anh)
    if anh is None:
        return None

    anh_resize = cv2.resize(anh, (500, 500))
    anh_lammin = cv2.GaussianBlur(anh_resize, (5, 5), 0)
    hsv = cv2.cvtColor(anh_lammin, cv2.COLOR_BGR2HSV)

    # Tách lá
    nguong_duoi = np.array([5, 30, 30])
    nguong_tren = np.array([100, 255, 255])
    matna_la = cv2.inRange(hsv, nguong_duoi, nguong_tren)

    kernel = np.ones((5, 5), np.uint8)
    matna_la = cv2.morphologyEx(matna_la, cv2.MORPH_CLOSE, kernel)

    dientich_la = cv2.countNonZero(matna_la)
    if dientich_la < 10000:
        return None

    # Vùng vàng
    matna_vang = cv2.inRange(hsv, (15, 60, 60), (35, 255, 255))
    matna_vang = cv2.bitwise_and(matna_vang, matna_la)
    tile_vang = cv2.countNonZero(matna_vang) / dientich_la

    # Vùng nâu cháy
    matna_nau = cv2.inRange(hsv, (0, 40, 40), (18, 255, 180))
    matna_nau = cv2.bitwise_and(matna_nau, matna_la)
    tile_nau = cv2.countNonZero(matna_nau) / dientich_la

    # Vùng xanh đậm
    matna_xanhdam = cv2.inRange(hsv, (40, 160, 20), (90, 255, 120))
    matna_xanhdam = cv2.bitwise_and(matna_xanhdam, matna_la)
    tile_xanhdam = cv2.countNonZero(matna_xanhdam) / dientich_la

    # Phân tích gân lá
    anh_xam = cv2.cvtColor(anh_resize, cv2.COLOR_BGR2GRAY)
    canh = cv2.Canny(anh_xam, 100, 200)
    canh_tren_la = cv2.bitwise_and(canh, matna_la)
    matdo_ganla = cv2.countNonZero(canh_tren_la) / dientich_la

    du_doan = []

    # Lá khỏe
    if tile_vang < 0.1 and tile_nau < 0.05 and tile_xanhdam < 0.1:
        return ["Lá khỏe mạnh"]

    if tile_nau > 0.1:
        du_doan.append('Potassium (K)')

    if tile_vang > 0.15:
        if matdo_ganla > 0.06:
            du_doan.append('Magnesium (Mg)')
            du_doan.append('Iron (Fe)')
        else:
            du_doan.append('Nitrogen (N)')

    if tile_xanhdam > 0.15:
        du_doan.append('Phosphorus (P)')

    du_doan = list(dict.fromkeys(du_doan))
    return du_doan if du_doan else ["Không xác định rõ - Cần thêm dữ liệu"]


@app.route('/uploads/<tenfile>')
def hien_thi_anh(tenfile):
    return send_from_directory(app.config['THU_MUC_TAI_LEN'], tenfile)


@app.route('/', methods=['GET', 'POST'])
def trang_chinh():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('Lỗi: Không tìm thấy tệp tin.')
            return render_template('web.html')

        tep = request.files['file']

        if tep.filename == '':
            flash('Lỗi: Bạn chưa chọn ảnh.')
            return render_template('web.html')

        if tep and kiemtra_dinhdang(tep.filename):

            ten_file = secure_filename(tep.filename)
            duongdan = os.path.join(app.config['THU_MUC_TAI_LEN'], ten_file)
            tep.save(duongdan)

            ketqua_du_doan = phan_tich_la(duongdan)

            if ketqua_du_doan is None:
                flash('Lỗi: Ảnh không rõ nét hoặc không tìm thấy lá.')
                return render_template('web.html')

            ketqua = []

            for chat in ketqua_du_doan:
                if chat in thongtin_chat:
                    ketqua.append({
                        'tenchat': chat,
                        'trieuchung': thongtin_chat[chat]['trieu_chung'],
                        'goi_y_bosung': thongtin_chat[chat]['goi_y_bosung']
                    })
                else:
                    ketqua.append({
                        'tenchat': chat,
                        'trieuchung': 'Bình thường',
                        'goi_y_bosung': 'Tiếp tục chăm sóc'
                    })

            return render_template('web.html', results=ketqua, image_file=ten_file)

        flash('Lỗi: Định dạng ảnh không hỗ trợ.')

    return render_template('web.html')


if __name__ == '__main__':
    app.run()