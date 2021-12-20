from flask import Flask, render_template
import plotly.graph_objs as go
import plotly

app = Flask(__name__)

@app.route('/plot')
def plot():
    x_vals = ['lions', 'tigers', 'bears']
    y_vals = [6,11,3]
    bars_data = go.Bar(
        x = x_vals,
        y = y_vals
    )
    fig = go.Figure(data=bars_data)
    div = fig.to_html(full_html=False)
    return render_template("plot.html", plot_div=div)

if __name__ == "__main__":
    app.run(debug=True)