
chart_head = '''
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<script src="https://code.highcharts.com/stock/modules/data.js"></script>
<script src="https://code.highcharts.com/stock/modules/exporting.js"></script>
<script src="https://code.highcharts.com/stock/modules/export-data.js"></script>
'''

chart_pattern = '''
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
