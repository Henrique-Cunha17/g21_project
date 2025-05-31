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
from sqlalchemy import create_engine, text
import datetime as dt
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Load database
db_path = os.path.abspath(os.path.join(filename, 'App.db'))
for cls in [Carriers, Shipments, Shipment_details, Warehouses, Userlogin]:
    cls.read(db_path)

engine = create_engine(f'sqlite:///{db_path}')

def ensure_default_users_sqlalchemy():
    users = [
        (1, "admin", "admin", Userlogin.set_password("1234")),
        (2, "user1", "users", Userlogin.set_password("12345"))
    ]
    with engine.connect() as conn:
        for id, user, usergroup, password in users:
            result = conn.execute(
                text("SELECT COUNT(*) FROM Userlogin WHERE id = :id"),
                {"id": id}
            )
            if result.scalar() == 0:
                conn.execute(
                    text("INSERT INTO Userlogin (id, user, usergroup, password) VALUES (:id, :user, :usergroup, :password)"),
                    {"id": id, "user": user, "usergroup": usergroup, "password": password}
                )
        conn.commit()

ensure_default_users_sqlalchemy()
Userlogin.read(db_path) # Ensure Userlogin is loaded

def get_common_data(cls, option: str) -> Tuple[str, str, Dict[str, str]]:
    butshow, butedit = "", "disabled"
    fields = {f[1:]: "" for f in cls.att}

    try:
        cls.lst = getattr(cls, 'lst', [])
        cls.pos = getattr(cls, 'pos', -1)

        if option == 'exit':
            session['filter_date'] = request.form.get('filter_date', '') or request.args.get('filter_date', '')
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

    # Lê o filtro da data do formulário ou mantém o valor anterior/default
    if request.method == "POST":
        filter_date = request.form.get("filter_date")
    else:
        filter_date = request.args.get("filter_date") or dt.datetime.strptime("2025-02-18", "%Y-%m-%d").date().isoformat()

    # DataFrame de envios
    df_shipments = pd.DataFrame([
        {
            "shipment_id": s.shipment_id,
            "status": s.status,
            "origin": s.origin,
            "destination": s.destination,
            "shipment_date": s.shipment_date,
            "tracking_number": s.tracking_number
        }
        for s in Shipments.obj.values()
    ])

    # Filtra pelo dia exato
    if filter_date:
        df_shipments = df_shipments[df_shipments["shipment_date"].astype(str) == filter_date]

    status_counts = df_shipments.groupby("status").size().reset_index(name="count")

    # Gráfico circular (pie chart)
    fig = px.pie(
        status_counts,
        names="status",
        values="count",
        color_discrete_sequence=["#7da6d9", "#8e9194", "#f1f4fa"],
    )

    fig.update_traces(
        textinfo='percent+label',
        marker=dict(line=dict(color='#2c3e50', width=2))
    )
    fig.update_layout(
        plot_bgcolor="#2c3e50",
        paper_bgcolor="#2c3e50",
        font=dict(
            family="Mulish, sans-serif",
            color="#f1f4fa",
            size=16
        ),
        title_font=dict(
            family="Cal Sans, sans-serif",
            color="#f1f4fa",
            size=22
        ),
        legend=dict(
            font=dict(color="#f1f4fa"),
            bgcolor="#2c3e50"
        )
    )

    plot_html = fig.to_html(full_html=False)

    # Atualiza status se pedido
    if request.method == "POST":
        change_status_id = request.form.get("change_status_id")
        new_status = request.form.get("new_status")
        shipment = Shipments.obj.get(change_status_id)
        if not shipment:
            try:
                shipment = Shipments.obj.get(int(change_status_id))
            except Exception:
                shipment = None
        if change_status_id and new_status and shipment:
            shipment.status = new_status
            Shipments.update_status_in_db(change_status_id, new_status)
            Shipments.read(db_path)

    # Filtra as listas conforme o filtro de data e status
    def filter_shipments(status):
        return [
            obj for obj in Shipments.obj.values()
            if getattr(obj, "status", None) == status and
               (not filter_date or str(getattr(obj, "shipment_date", "")) == filter_date)
        ]

    delivered_shipments = filter_shipments("Delivered")
    in_transit_shipments = filter_shipments("In Transit")

    # --- Top 3 carriers do dia selecionado ---
    # Junta todos os shipments do dia selecionado
    shipments_in_day = [
        obj for obj in Shipments.obj.values()
        if str(getattr(obj, "shipment_date", "")) == filter_date
    ]
    # Conta as encomendas por carrier_id (usando Shipment_details)
    carrier_count = {}
    for shipment in shipments_in_day:
        for detail in Shipment_details.obj.values():
            if str(detail.shipment_id) == str(shipment.shipment_id):
                carrier_id = detail.carrier_id
                carrier_count[carrier_id] = carrier_count.get(carrier_id, 0) + 1
    # Ordena e apanha o top 3
    top_carriers = sorted(carrier_count.items(), key=lambda x: x[1], reverse=True)[:3]
    
    top_carriers_info = []
    for carrier_id, count in top_carriers:
        carrier = Carriers.obj.get(carrier_id)
        carrier_name = carrier.name if carrier else str(carrier_id)
        top_carriers_info.append({"carrier_id": carrier_id, "name": carrier_name, "count": count})

    return render_template(
        "index.html",
        ulogin=session.get("user"),
        delivered_shipments=sorted(delivered_shipments, key=lambda x: int(x.shipment_id)),
        in_transit_shipments=sorted(in_transit_shipments, key=lambda x: int(x.shipment_id)),
        filter_date=filter_date,
        plot_html=plot_html,
        top_carriers_info=top_carriers_info
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

@app.route("/map")
def map():
    warehouses = []
    for w in Warehouses.obj.values():
        warehouses.append({
            "id": w.warehouse_id,
            "location": w.location,
            "lat": w.latitude,
            "lon": w.longitude,
            "capacity": w.capacity
        })
    return render_template("map.html", warehouses=warehouses)

if __name__ == '__main__':
    app.run(debug=True)
