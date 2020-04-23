
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
            buttons: [{{
                type: 'hour',
                count: 1,
                text: '1h'
            }}, {{
                type: 'day',
                count: 1,
                text: '1D'
            }}, {{
                type: 'all',
                count: 1,
                text: 'All'
            }}],
            selected: 1,
            inputEnabled: true
        }},
        title: {{
            text: '{chart_name}'
        }},
        colors: ['#FF0000', '#000000', '#000000', '#000000', '#000000',
        '#000000', '#000000', '#000000', '#000000', '#000000'],
        series: [{{
            name: '{series_name}',
            type: 'area',
            gapSize: 5,
            data: data,
            tooltip: {{
                valueDecimals: 5
            }},
            fillColor: {{
                linearGradient: {{
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1,
                }},
                stops: [
                    [0, "rgba(0,0,0,1)"],
                    [1, "rgba(0,0,0,0.6)"]
                ]
            }},
            threshold: null
        }}]
    }});
}});
Highcharts.setOptions(Highcharts.theme);

</script>
<div id='{chart_id}' style="height: 400px; min-width: 310px"></div>

'''
