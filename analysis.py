
import pandas as pd
import matplotlib.pyplot as plt

def plot_material_bars_from_excel(
    file_path: str,
    sheet_name: str = "25",
    start_date: str = "2025-04-01",
    periods: int = 12,
    width: int = 20,
    figsize=(16, 5)
):
    """
    Plots monthly bar charts for each material from an Excel sheet.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    labels = df["FY25"].astype(str) + " - " + df["Material"].astype(str)
    df_numeric = df.drop(columns=["FY25", "Material"]).iloc[:, :periods]
    custom_timestamps = pd.date_range(start=start_date, periods=periods, freq="MS")

    # inside plot_material_bars_from_excel()

    for i in range(len(df_numeric)):
        values = pd.to_numeric(df_numeric.iloc[i], errors="coerce")
        label = labels.iloc[i]

        if pd.Series(values).sum() > 0:
            plt.figure(figsize=figsize)
            plt.bar(custom_timestamps[:len(values)], values, width=width)
            plt.title(label)
            plt.xlabel("Timestamp")
            plt.ylabel("Value")
            plt.xticks(
                ticks=custom_timestamps,
                labels=custom_timestamps.strftime("%b-%Y"),
                rotation=45
            )
            plt.legend([label])
            plt.tight_layout()
            plt.show()


def main():
    # Call the plotting function with your file
    plot_material_bars_from_excel("pidsg25-05.xlsx")

if __name__ == '__main__':
    main()
