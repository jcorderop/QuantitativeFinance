import base64
import time
from datetime import datetime
from io import BytesIO

from flask import Blueprint, Response
from matplotlib.figure import Figure

plot = Blueprint('plot', __name__)
plot.url_prefix = '/plot'

@plot.route("/")
def hello():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

# https://stackoverflow.com/questions/13386681/streaming-data-with-python-and-flask
@plot.route('/time')
def doyouhavethetime():
    def generate():
        for i in range(10):
            yield "{}\n".format(datetime.now())
            time.sleep(1)
    return Response(generate(), mimetype='application/json')