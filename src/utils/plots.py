import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_stock(
    df,
    date_col: str = 'date',
    price_col: str = 'close',
    rsi: 'pd.Series | None' = None,
    indicators: dict = None
):
    """
    Plot stock price data with optional technical indicators using Plotly.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least date_col and price_col.
    date_col : str, default='date'
        Column name for x-axis.
    price_col : str, default='close'
        Column name for y-axis (main price line).
    indicators : dict, optional
        Dictionary of additional lines to plot.
        Example:
            {
                'rolling_avg': {'data': df['close'].rolling(15).mean(), 'color': 'red'},
                'upper_band': {'data': upper_band, 'color': 'green', 'dash': 'dot'}
            }
    title : str, optional
        Chart title.

    Returns
    -------
    plotly.graph_objects.Figure
        The Plotly figure object (can be shown or saved).
    """

    # get symbol
    symbol = np.unique(df['symbol'])

    if len(symbol) != 1:
        print('Error: Too many symbols of data passed to plot_stock - please filter df to a single stock before running function')
    else:
        symbol = symbol[0]
    
    fig = go.Figure()

    # Main price trace
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[price_col],
        name='Price',
        mode='lines+markers',
        line=dict(color='black', width=2)
    ))

    # Optional indicators
    if indicators:
        for name, params in indicators.items():
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=params['data'],
                name=name,
                mode='lines',
                line=dict(
                    color=params.get('color', 'blue'),
                    width=params.get('width', 1.5),
                    dash=params.get('dash', 'solid')
                )
            ))

    # Layout
    fig.update_layout(
        title= f'Stock Price for: {symbol}',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        legend=dict(x=0.01, y=0.99),
        template='plotly_white'
    )

    return fig
