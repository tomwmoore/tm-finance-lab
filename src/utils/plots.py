import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

def plot_stock(
    df,
    date_col: str = 'date',
    price_col: str = 'close',
    rsi: 'pd.Series | None' = None,
    indicators: dict = None,
    plot_volume: bool = False
):
    """
    Plot stock price data with optional RSI, indicators, and volume using Plotly.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least date_col, price_col, and optionally 'volume'.
    date_col : str, default='date'
        Column name for x-axis.
    price_col : str, default='close'
        Column name for y-axis (main price line).
    rsi : pd.Series, optional
        RSI values to plot in a separate subplot.
    indicators : dict, optional
        Dictionary of additional lines to plot on the price chart.
    plot_volume : bool, default=False
        Whether to add a subplot showing trading volume as a bar chart.

    Returns
    -------
    plotly.graph_objects.Figure
        The Plotly figure object.
    """

    symbol = np.unique(df['symbol'])
    if len(symbol) != 1:
        print('Error: Too many symbols of data passed to plot_stock - please filter df to a single stock before running function')
        return
    else:
        symbol = symbol[0]

    has_rsi = rsi is not None
    has_volume = plot_volume and 'volume' in df.columns


    # determine subplot layout
    nrows = 1 + int(has_rsi) + int(has_volume)
    row_heights = []
    subplot_titles = None

    # main plot always first
    if has_rsi and has_volume:
        row_heights = [0.6, 0.25, 0.15]
        # subplot_titles += ["RSI (Relative Strength Index)", "Volume"]
    elif has_rsi:
        row_heights = [0.7, 0.3]
        # subplot_titles += ["RSI (Relative Strength Index)"]
    elif has_volume:
        row_heights = [0.75, 0.25]
        # subplot_titles += ["Volume"]
    else:
        row_heights = [1]

    fig = make_subplots(
        rows=nrows,
        cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.05,
        subplot_titles=None
    )

    # --- Price trace ---
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[price_col],
            name='Price',
            mode='lines+markers',
            line=dict(color='black', width=2)
        ),
        row=1, col=1
    )

    # --- Indicators ---
    if indicators:
        for name, params in indicators.items():
            fig.add_trace(
                go.Scatter(
                    x=df[date_col],
                    y=params['data'],
                    name=name,
                    mode='lines',
                    line=dict(
                        color=params.get('color', 'blue'),
                        width=params.get('width', 1.5),
                        dash=params.get('dash', 'solid')
                    )
                ),
                row=1, col=1
            )

    # --- RSI subplot ---
    current_row = 2 if has_rsi else 1
    if has_rsi:
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=rsi,
                mode='lines',
                line=dict(color='orange', width=1.5),
                name='RSI'
            ),
            row=current_row, col=1
        )

        fig.add_hline(y=70, line_dash='dot', line_color='red', row=current_row, col=1)
        fig.add_hline(y=30, line_dash='dot', line_color='green', row=current_row, col=1)
        fig.update_yaxes(title_text="RSI (0-100)", range=[0, 100], row=current_row, col=1)

    # --- Volume subplot ---
    if has_volume:
        vol_row = nrows  # always last
        fig.add_trace(
            go.Bar(
                x=df[date_col],
                y=df['volume'],
                name='Volume',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=vol_row, col=1
        )
        fig.update_yaxes(title_text="Volume", row=vol_row, col=1)

    # --- Layout ---
    fig.update_layout(
        height= 350 + (200 if has_rsi else 0) + (150 if has_volume else 0),
        title={
            'text': f"Stock Overview – {symbol}",
            'x': 0.5, 
            'pad': {'b': 20},
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis=dict(title='Price'),
        template='plotly_white',
        legend=dict(
            orientation='h',          # horizontal legend
            yanchor='bottom',         # anchor to bottom of legend box
            y=1.0,                  
            xanchor='center',         # center align
            x=0.5,                    # horizontally centered
            bgcolor='rgba(255,255,255,0)',
            bordercolor='rgba(0,0,0,0)',
            font=dict(size=10)
        )
    )

    # --- X-axis titles ---
    fig.update_xaxes(title_text="Date", row=nrows, col=1)

    return fig
