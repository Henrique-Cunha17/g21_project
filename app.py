from flask import Flask, render_template, request, session, redirect, url_for, Response
from classes.Carriers import Carriers
from classes.Shipments import Shipments
from classes.Shipment_details import Shipment_details
from classes.Warehouses import Warehouses
from classes.userlogin import Userlogin
from subs.apps_userlogin import apps_userlogin
from typing import Tuple, Dict
from collections import Counter
from datafile import filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Load database
db_path = os.path.abspath(os.path.join(filename, 'App.db'))
for cls in [Carriers, Shipments, Shipment_details, Warehouses]:
    cls.read(db_path)

def get_common_data(cls, option: str) -> Tuple[str, str, Dict[str, str]]:
    butshow, butedit = "", "disabled"
    fields = {f[1:]: "" for f in cls.att}

    try:
        cls.lst = getattr(cls, 'lst', [])
        cls.pos = getattr(cls, 'pos', -1)

        if option == 'exit':
            return redirect(url_for('index'))

        prev_option = session.get('prev_option', '')
        session['prev_option'] = option

        if option == "insert":
            fields = {f[1:]: "" for f in cls.att}
            cls.pos = -1
            return "disabled", "", fields

        if option == "save":
            if prev_option == "insert":
                values = [request.form.get(f[1:], "") for f in cls.att]
                obj = cls.from_string(";".join(values))
                cls.insert(getattr(obj, cls.att[0]))
                cls.read(db_path)  # Reload after insertion
                cls.pos = len(cls.lst) - 1
                obj = cls.current()
                fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}
                return "", "disabled", fields

            elif prev_option == "edit":
                obj = cls.current()
                if obj:
                    for f in cls.att[1:]:
                        setattr(obj, f, request.form.get(f[1:], ""))
                    cls.update(getattr(obj, cls.att[0]))
                    fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}
                    return "", "disabled", fields

        if option == "delete":
            if cls.lst and 0 <= cls.pos < len(cls.lst):
                cls.remove(cls.lst[cls.pos])
                cls.read(db_path)  # Refresh data
                if cls.lst:
                    cls.pos = min(cls.pos, len(cls.lst) - 1)
                    obj = cls.current()
                    if obj:
                        fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}
                else:
                    cls.pos = -1
                    fields = {f[1:]: "" for f in cls.att}
                return butshow, butedit, fields

        if option in ["first", "previous", "next", "last", "reload"]:
            if cls.lst:
                getattr(cls, option if option != "reload" else "first")()
                obj = cls.current()
                if obj:
                    fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}

        if option == "edit":
            if cls.lst and 0 <= cls.pos < len(cls.lst):
                obj = cls.current()
                if obj:
                    fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}
                    return "disabled", "", fields

        if cls.lst and 0 <= cls.pos < len(cls.lst):
            obj = cls.current()
            if obj:
                fields = {f[1:]: str(getattr(obj, f)) for f in cls.att}

    except Exception as e:
        print(f"Error in get_common_data: {e}")
        cls.lst = getattr(cls, 'lst', [])
        cls.pos = max(-1, min(getattr(cls, 'pos', -1), len(cls.lst) - 1))
        fields = {f[1:]: str(getattr(cls.current(), f)) for f in cls.att} if cls.lst else fields

    return butshow, butedit, fields

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("user"):
        return redirect(url_for("login"))

    filter_date = None

    # Atualiza status se necessário
    if request.method == "POST":
        change_status_id = request.form.get("change_status_id")
        new_status = request.form.get("new_status")
        if change_status_id and new_status:
            shipment = Shipments.obj.get(change_status_id)
            if shipment:
                shipment.status = new_status
                Shipments.update_status_in_db(change_status_id, new_status)
                Shipments.read(db_path)
        filter_date = request.form.get("filter_date")

    # Filtra as listas conforme o filtro de data
    def filter_shipments(status):
        return [
            obj for obj in Shipments.obj.values()
            if getattr(obj, "status", None) == status and
               (not filter_date or str(getattr(obj, "shipment_date", "")) == filter_date)
        ]

    delivered_shipments = filter_shipments("Delivered")
    in_transit_shipments = filter_shipments("In Transit")

    return render_template(
        "index.html",
        ulogin=session.get("user"),
        delivered_shipments=delivered_shipments,
        in_transit_shipments=in_transit_shipments,
        filter_date=filter_date
    )

@app.route("/login")
def login():
    return render_template("login.html", user= "", password="", ulogin=session.get("user"),resul = "")

@app.route("/logoff")
def logoff():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/chklogin", methods=["POST", "GET"])
def chklogin():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]
        resul = Userlogin.chk_password(user, password)
        if resul == "Valid":
            session["user"] = user
            return redirect(url_for("index"))
        return render_template("login.html", user=user, password=password, ulogin=session.get("user"), resul=resul)
    return render_template("login.html", user="", password="", ulogin=session.get("user"), resul="")

@app.route("/Userlogin", methods=["POST","GET"])
def userlogin():
    return apps_userlogin()

@app.route("/carriers", methods=["GET", "POST"])
def carriers():
    option = request.args.get("option", "")
    if request.method == "POST":
        option = "save"
    result = get_common_data(Carriers, option)
    if isinstance(result, Response):
        return result
    butshow, butedit, fields = result
    return render_template("carriers.html", butshow=butshow, butedit=butedit, fields=fields, ulogin=session.get("user"))

@app.route("/shipments", methods=["GET", "POST"])
def shipments():
    option = request.args.get("option", "")
    if request.method == "POST":
        option = "save"
    result = get_common_data(Shipments, option)
    if isinstance(result, Response):
        return result
    butshow, butedit, fields = result
    return render_template("shipments.html", butshow=butshow, butedit=butedit, fields=fields, ulogin=session.get("user"))

@app.route("/shipment_details", methods=["GET", "POST"])
def shipment_details():
    option = request.args.get("option", "")
    if request.method == "POST":
        option = "save"
    result = get_common_data(Shipment_details, option)
    if isinstance(result, Response):
        return result
    butshow, butedit, fields = result
    return render_template("shipment_details.html", butshow=butshow, butedit=butedit, fields=fields, ulogin=session.get("user"))

@app.route("/warehouses", methods=["GET", "POST"])
def warehouses():
    option = request.args.get("option", "")
    if request.method == "POST":
        option = "save"
    result = get_common_data(Warehouses, option)
    if isinstance(result, Response):
        return result
    butshow, butedit, fields = result
    return render_template("warehouses.html", butshow=butshow, butedit=butedit, fields=fields, ulogin=session.get("user"))



@app.route("/statistics", methods=["GET", "POST"])
def statistics():
    class_map = {
        "Carriers": Carriers,
        "Shipments": Shipments,
        "Shipment_details": Shipment_details,
        "Warehouses": Warehouses
    }

    attributes = {}
    data_labels = []
    data_counts = []
    selected_class = ""
    selected_attr = ""

    if request.method == "POST":
        selected_class = request.form.get("class")
        selected_attr = request.form.get("attribute")

        cls = class_map.get(selected_class)
        if cls and hasattr(cls, "lst") and hasattr(cls, "obj"):

            try:
                index = cls.des.index(selected_attr)
                internal_attr = cls.att[index]

                values = [
                    str(getattr(cls.obj[obj_id], internal_attr, "Unknown"))
                    for obj_id in cls.lst
                    if obj_id in cls.obj
                ]

                counter = Counter(values)
                most_common = counter.most_common(10)
                data_labels = [label for label, _ in most_common]
                data_counts = [count for _, count in most_common]

            except (ValueError, IndexError, AttributeError) as e:
                print("Error resolving attribute:", e)

    for class_name, cls in class_map.items():
        if hasattr(cls, "des"):
            attributes[class_name] = cls.des

    return render_template(
        "statistics.html",
        class_names=list(class_map.keys()),
        attributes=attributes,
        selected_class=selected_class,
        selected_attr=selected_attr,
        labels=data_labels,
        counts=data_counts,
        ulogin=session.get("user")
    )

if __name__ == '__main__':
    app.run(debug=True)
