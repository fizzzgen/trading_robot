from flask import Flask, make_response
import json
import sqlite3
from conf import config
from resources import constants


def get_conn_cur():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    return conn, cur

app = Flask(__name__)


class ChartDescription(object):
    def __init__(data_url, chart_name, chart_series_name):
        self.data_url = data_url
        self.chart_name = chart_name
        self.chart_series_name = chart_series_name


class HtmlDashCreator(object):
    def __init__(self):

        self.html = constants.chart_head
        self.chart_counter = 1


    def add_chart(self, chart_description):
        data_url = chart_description.data_url
        chart_name = chart_description.chart_name
        chart_series_name = chart_description.chart_series_name
        chart_id = self.chart_counter
        self.chart_counter += 1
        template = constants.chart_pattern
        self.html += template.format(
            chart_id=chart_id,
            chart_name=chart_name,
            series_name=chart_series_name,
            data_url=data_url
        )

    def render():
        return self.html


class ChartDescription(object):
    def __init__(self, data_url, chart_name, chart_series_name):
        self.data_url = data_url
        self.chart_name = chart_name
        self.chart_series_name = chart_series_name


CHARTS = [
    ChartDescription("engine_ping", "engine_ping", "engine_ping"),
    ChartDescription("balance", "balance", "balance"),
]

CHARTS2 = [
    ChartDescription("engine_ping", "engine_ping", "engine_ping"),
    ChartDescription("balance", "balance", "balance"),
]

FRAMES = [
    '/dashboard',
    '/dashboard2',
]


@app.route("/engine_ping")
def _engine_ping():
    conn, cur = get_conn_cur()
    cur.execute('SELECT ts, value FROM ping;')
    return json.dumps(cur.fetchall())


@app.route("/balance")
def _balance():
    conn, cur = get_conn_cur()
    cur.execute('SELECT ts, value FROM balance')
    return json.dumps(cur.fetchall())


@app.route("/dashboard")
def _dash():
    dashboard = HtmlDashCreator()
    for chart in CHARTS:
        dashboard.add_chart(chart)
    return dashboard.html


@app.route("/dashboard2")
def _dash2():
    dashboard = HtmlDashCreator()
    for chart in CHARTS2:
        dashboard.add_chart(chart)
    return dashboard.html


@app.route("/dashboard_framed")
def _dash_framed():
    html = '''<!DOCTYPE html>
    <html>

    <frameset cols="50%,*">
    <frame src="{frame1}">
    <frame src="{frame2}">
    </frameset>

    </html>
    '''.format(frame1=FRAMES[0], frame2=FRAMES[1])
    return html


if __name__ == "__main__":
    app.run(host='0.0.0.0')
