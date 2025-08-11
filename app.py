from flask import Flask, render_template, request, jsonify, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import os
import time

app = Flask(__name__)
STATIC_FOLDER = 'static'
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['STATIC_FOLDER'] = STATIC_FOLDER

def tversky_educational_v2(A, B, alpha, beta, log):
    log.append({'type': 'start', 'text': f"▶️ شروع تحلیل شباهت بین دو مجموعه با α={alpha} و β={beta}."})
    
    # نمایش اولیه مجموعه‌ها
    log.append({'type': 'show_sets', 'setA': sorted(list(A)), 'setB': sorted(list(B))})
    
    # مرحله ۱: پیدا کردن اشتراک
    intersection_set = A & B
    intersection_size = len(intersection_set)
    log.append({'type': 'animate_intersection', 'text': f"1️⃣ ابتدا اعضای مشترک (اشتراک) را پیدا می‌کنیم.", 'elements': sorted(list(intersection_set))})
    log.append({'type': 'calculation', 'variable': 'intersection', 'value': intersection_size, 'text': f"تعداد اعضای مشترک: {intersection_size}"})
    
    # مرحله ۲: پیدا کردن اعضای منحصر به فرد A
    only_A_set = A - B
    only_A_size = len(only_A_set)
    log.append({'type': 'animate_difference', 'set_name': 'A', 'text': f"2️⃣ سپس اعضایی که فقط در مجموعه A هستند را جدا می‌کنیم.", 'elements': sorted(list(only_A_set))})
    log.append({'type': 'calculation', 'variable': 'only_A', 'value': only_A_size, 'text': f"تعداد اعضای فقط در A: {only_A_size}"})

    # مرحله ۳: پیدا کردن اعضای منحصر به فرد B
    only_B_set = B - A
    only_B_size = len(only_B_set)
    log.append({'type': 'animate_difference', 'set_name': 'B', 'text': f"3️⃣ و بعد اعضایی که فقط در مجموعه B هستند را جدا می‌کنیم.", 'elements': sorted(list(only_B_set))})
    log.append({'type': 'calculation', 'variable': 'only_B', 'value': only_B_size, 'text': f"تعداد اعضای فقط در B: {only_B_size}"})
    
    # مرحله ۴: نمایش فرمول
    log.append({'type': 'show_formula', 'text': "4️⃣ اکنون مقادیر محاسبه شده را در فرمول تورسکی قرار می‌دهemo."})
    
    # مرحله ۵: جایگذاری مقادیر در فرمول
    log.append({'type': 'substitute_values', 'text': "جایگذاری اعداد در فرمول..."})

    # مرحله ۶: محاسبه نهایی
    denominator = intersection_size + alpha * only_A_size + beta * only_B_size
    log.append({'type': 'calculate_denominator', 'value': denominator, 'text': f"5️⃣ ابتدا مخرج کسر را محاسبه می‌کنیم: {intersection_size} + {alpha}×{only_A_size} + {beta}×{only_B_size} = {denominator}"})
    
    if denominator == 0:
        similarity = 0.0
        log.append({'type': 'final_result', 'value': similarity, 'text': "⚠️ چون مخرج صفر است، نتیجه نهایی صفر می‌باشد."})
    else:
        similarity = intersection_size / denominator
        log.append({'type': 'final_result', 'value': round(similarity, 4), 'text': f"6️⃣ در نهایت با تقسیم صورت بر مخرج، به نتیجه نهایی می‌رسیم: {intersection_size} / {denominator} ≈ {similarity:.4f}"})
    
    log.append({'type': 'show_venn', 'text': "و در انتها، نمودار ون این دو مجموعه را به عنوان خلاصه مشاهده می‌کنید."})
    
    return similarity, only_A_size, only_B_size, intersection_size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate_tversky', methods=['POST'])
def calculate_api():
    try:
        data = request.json
        set_a_str, set_b_str = data.get('setA', ''), data.get('setB', '')
        alpha, beta = float(data.get('alpha', 1.0)), float(data.get('beta', 1.0))

        A = set(item.strip() for item in set_a_str.split(',') if item.strip())
        B = set(item.strip() for item in set_b_str.split(',') if item.strip())
        
        log = []
        similarity, only_a_size, only_b_size, intersection_size = tversky_educational_v2(A, B, alpha, beta, log)

        plt.figure(figsize=(6, 6))
        venn2(subsets=(only_a_size, only_b_size, intersection_size), set_labels=('مجموعه A', 'مجموعه B'))
        
        unique_filename = f'venn_{int(time.time())}.png'
        filepath = os.path.join(STATIC_FOLDER, unique_filename)
        plt.savefig(filepath, transparent=False, facecolor='#f0f2f5', bbox_inches='tight')
        plt.close()
        
        image_url = url_for('static', filename=unique_filename)
        
        return jsonify({'success': True, 'similarity': similarity, 'imageUrl': image_url, 'log': log})
    except Exception as e:
        return jsonify({'success': False, 'error': f'خطا: {str(e)}'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
    