from flask import Flask, make_response
app = Flask(__name__)


class ChartDescription(object):
    def __init__(data_url, chart_name, chart_series_name):
        self.data_url = data_url
        self.chart_name = chart_name
        self.chart_series_name = chart_series_name


class HtmlDashCreator(object):
    def __init__(self):

        self.html = '''
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/stock/modules/data.js"></script>
<script src="https://code.highcharts.com/stock/modules/exporting.js"></script>
<script src="https://code.highcharts.com/stock/modules/export-data.js"></script>
'''
        self.chart_counter = 1


    def add_chart(self, chart_description):
        data_url = chart_description.data_url
        chart_name = chart_description.chart_name
        chart_series_name = chart_description.chart_series_name
        chart_id = self.chart_counter
        self.chart_counter += 1
        template = '''
<script>

Highcharts.getJSON('{data_url}', function (data) {{
    // Create the chart
    Highcharts.stockChart('{chart_id}', {{


        rangeSelector: {{
            selected: 1
        }},

        title: {{
            text: '{chart_name}'
        }},

        series: [{{
            name: '{series_name}',
            data: data,
            tooltip: {{
                valueDecimals: 5
            }}
        }}]
    }});
}});
Highcharts.setOptions(Highcharts.theme);

</script>
<div id='{chart_id}' style="height: 400px; min-width: 310px"></div>

'''
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
    ChartDescription("chart1data", "test", "test series"),
    ChartDescription("chart1data", "test", "test series"),
    ChartDescription("chart1data", "test", "test series"),
    ChartDescription("chart1data", "test", "test series"),
]

FRAMES = [
    '/dashboard',
    '/dashboard',
]


@app.route("/chart1data")
def simple():
    
    return "[[1,1],[2,2],[3,3],[4,4]]"


@app.route("/dashboard")
def dash():
    dashboard = HtmlDashCreator()
    for chart in CHARTS:
        dashboard.add_chart(chart)
    return dashboard.html

@app.route("/dashboard_framed")
def dash_framed():
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
    app.run()