from flask import abort, Flask, request, redirect, render_template, url_for
import requests

# ================== # Info # ================== #

app = Flask(__name__, static_folder="static")

API_KEY = "" # API_KEY NextPay
TOKEN = ""  # Token Bot
BACK_URL = ""
headers = {
    'User-Agent': 'PostmanRuntime/7.26.8',
    'Content-Type': 'application/x-www-form-urlencoded'
}

my_user_id = []

text_succ = '✅ پرداخت با موفقیت انجام شد.\n\n💰 مبلغ {} تومان به موجودی شما اضافه گردید.\nکد پیگیری تراکنش: {}'

text_error = '❌ خطا در تراکنش\nکد پیگیری تراکنش: {}'

# ================== # Filter IP (IRAN) # ================== #


def check_ip(ip):
    resp = requests.get(f"http://ip-api.com/json/{ip}").json()
    return True if resp['country'] == "Iran" else False

# ================== # Send Message # ================== #


def send_message(code, trans_id):
    print("Code: ",code)
    global my_user_id
    for usr in my_user_id:
        if usr["trans_id"] == trans_id:
            user = usr["user_id"]
    if code == "0":
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={user}&text={text_succ.format(usr["amount"],usr["trans_id"])}'
    else:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={user}&text={text_error.format(usr["trans_id"])}'
    try:
        requests.get(url, timeout=3)
        return True
    except:
        return False

# ================== # Home # ================== #


@app.route("/", methods=['GET'])
def home():
    if not check_ip(request.remote_addr):
        context = {
            "ip": request.remote_addr
        }
        return render_template("index.html", **context)

    return "Telegram : @Hidden0612 :)"

# ================== # Verify Payment # ================== #


@app.route("/verify/", methods=["GET"])
def verify():
    if not request.args:
        return render_template("404.html")
    trans_id = request.args["trans_id"]
    amount = request.args["amount"]
    url_stat = "https://nextpay.org/nx/gateway/verify"
    data = {
        "api_key": API_KEY,
        "trans_id": trans_id,
        "amount": amount,
    }
    resp = requests.post(url_stat, data=data, headers=headers).json()

    if resp["code"]:
        context = {
            "code": resp["code"],
            "Shaparak_Ref_Id": resp["Shaparak_Ref_Id"]
        }
        send_message(resp["code"], trans_id)
        return render_template("verify.html", **context)

# ================== # Redirect Payment # ================== #


@app.route("/data/", methods=["GET"])
def check():
    global my_user_id
    if not check_ip(request.remote_addr):
        context = {
            "ip": request.remote_addr
        }
        return render_template("index.html", **context)
    if not request.args:
        return render_template("404.html")

    user_id = request.args["chat_id"]
    amount = request.args["amount"]
    number = request.args["number"]

    url = "https://nextpay.org/nx/gateway/token"

    payload = fr'api_key={API_KEY}&amount={amount}&order_id=85NX85s427&customer_phone={number}&custom_json_fields=%7B%20%22productName%22%3A%22Shoes752%22%20%2C%20%22id%22%3A52%20%7D&callback_uri={BACK_URL}'
    response = requests.request(
        "POST", url, headers=headers, data=payload).json()

    re_url = f"https://nextpay.org/nx/gateway/payment/{response['trans_id']}"
    my_user_id.append(
        {"user_id": user_id, "trans_id": response['trans_id'], "amount": amount})
    return redirect(re_url)

# ================== # Error 404 # ================== #


@app.errorhandler(404)
def error404(error):
    return render_template("404.html") , 404


# ================== # Run # ================== #
if __name__ == "__main__":
    app.run("0.0.0.0")
