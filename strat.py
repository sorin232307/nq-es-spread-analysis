import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="darkgrid")
plt.rcParams['figure.figsize'] = (14, 10)


def run_strategy():

    tickers = ['QQQ', 'SPY']


    df = yf.download(tickers, period='2y', interval='1h', progress=False, auto_adjust=True)


    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df['Close']
        except KeyError:
            df = df['Adj Close']

    df = df.dropna()

    #print("--- PREVIEW DATE ---")
    #print(df.head())
    #print(df.tail())
    #print(f"Total rânduri: {len(df)}")



    #A. Market Regime (Filter)
    df['Macro_Trend'] = df['QQQ'].ewm(span=200, adjust=False).mean()

    #1 = Bullish (Buy), 0 = Bearish(Wait)
    df['Market_Regime'] = np.where(df['QQQ'] > df['Macro_Trend'], 1, 0)

    #B. Statistical Reversion(z-score)
    df['Ratio'] = df['QQQ'] / df['SPY']

    window = 40
    rolling_mean = df['Ratio'].rolling(window).mean()
    rolling_std = df['Ratio'].rolling(window).std()

    df['Z-Score'] = (df['Ratio'] - rolling_mean) / rolling_std

    #C. Generate Signals
    df['Entry_Signal'] = np.where(
        (df['Market_Regime'] ==1) & (df['Z-Score'] < -2),
        1, 0
    )

    return df

def plot_performance(df):

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [2, 1, 0.5]})

    ax1.plot(df.index, df['QQQ'], label='Nasdaq-100 (1H)', color='#2c3e50', alpha=0.8)
    ax1.plot(df.index, df['Macro_Trend'], label='EMA 200 (Trend Filter)', color='orange', linestyle='--', linewidth=1.5)

    #1. Signals
    entries = df[df['Entry_Signal'] == 1]
    if not entries.empty:
        ax1.scatter(entries.index, entries['QQQ'], color='#00e600', marker = '^', s=120, zorder=5, edgecolors='black',
            label='Entry Signal')

    ax1.set_title('Trend Regime + Statistical Reversion', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.legend(loc='upper left')

    #2. Z-Score
    ax2.plot(df.index, df['Z-Score'], color='#2980b9', label='Spread Z-Score')
    ax2.axhline(-2, color='red', linestyle='--', label='Oversold Threshold (-2 std)')
    ax2.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax2.fill_between(df.index, df['Z-Score'], -2, where=(df['Z-Score'] <-2), color='red', alpha=0.3)
    ax2.set_ylabel('Z-Score')
    ax2.legend(loc='upper left')

    #3. Market Regime
    ax3.fill_between(df.index, 0, 1, where=(df['Market_Regime']==1), color='#27ae60', alpha=0.5,
                     label='Buliish Regime')
    ax3.set_yticks([])
    ax3.set_ylabel('Market_Regime')
    ax3.legend(loc='upper left')

    plt.tight_layout()

    plt.savefig('strategy_result.png')
    plt.show()

if __name__ == '__main__':
    data = run_strategy()
    plot_performance(data)







