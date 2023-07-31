import numpy as np
import pandas as pd
from scipy import stats
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


myPath = "/Users/david/Dropbox/Computing/Linux/Python/python_larder/"
myFile = "nerdle.py"
myCSV_File = "nerdle.csv"


def make_df(data, name1, name2):
    ### new df with desired columns
    df_data = data[[name1, name2]].copy()
    # print(df_data)

    ### add cumulative distribution columns
    df_data["cum_sum_A"] = df_data[name1].cumsum()
    df_data["cum_sum_B"] = df_data[name2].cumsum()

    df_data["cum_perc_A"] = df_data.cum_sum_A / df_data[name1].sum()
    df_data["cum_perc_B"] = df_data.cum_sum_B / df_data[name2].sum()

    # print(df_data)

    ### find difference between distributions and max diff to obtain statistic
    df_data["diff"] = (df_data["cum_perc_A"] - df_data["cum_perc_B"]).abs()
    # print(df_data)

    d_stat = df_data["diff"].max()
    print("D-stat = " + str(d_stat))

    return d_stat


### convert to numpy arrays (not really needed now)
### data1 = df_data["cum_perc_A"].to_numpy()
### data2 = df_data["cum_perc_B"].to_numpy()
### print(data1, data2)

### find statistics REDUNDANT
###  myStats = stats.ks_2samp(data1, data2)
###  print(myStats)


def make_raw_data(data, name):
    ### create raw data from frequency distibution ###
    raw_data = np.repeat(data["Bin"], data[name]).to_numpy()

    return raw_data


def get_KSstats(data, name1, name2):
    d_stat = make_df(data, name1, name2)

    raw_data1 = make_raw_data(data, name1)
    raw_data2 = make_raw_data(data, name2)

    myStats2 = stats.ks_2samp(raw_data1, raw_data2)
    print()
    print("Comparing " + str(name1) + " with " + str(name2))
    print(myStats2)
    my_pvalue = round(myStats2.pvalue, 8)
    print("D-stat = " + str(round(d_stat, 8)))
    print("pvalue = " + str(my_pvalue))
    return my_pvalue


def get_KSstats_totals(data, name1):
    raw_data1 = make_raw_data(data, name1)
    raw_data2 = get_totals_raw(data, name1)

    myStats2 = stats.ks_2samp(raw_data1, raw_data2)
    print()
    print("Comparing " + str(name1) + " with totals")
    print(myStats2)
    my_pvalue = round(myStats2.pvalue, 8)

    print("pvalue = " + str(my_pvalue))
    return my_pvalue


def create_output(list_names):
    nerdle_output = pd.DataFrame(columns=list_names)
    nerdle_output.insert(0, "names", list_names)
    nerdle_output.set_index("names", inplace=True)
    print(nerdle_output)
    return nerdle_output


def get_totals_raw(data, name):
    data_totals = data.drop(["Bin"], axis=1)
    data_totals["total"] = data_totals.sum(axis=1, numeric_only=True)
    print(data_totals)
    data_totals["total2"] = data_totals["total"] - data_totals[name]
    print(data_totals)

    raw_data = np.repeat(data["Bin"], data_totals["total2"]).to_numpy()
    print(raw_data)
    return raw_data


def get_mean_sd(data, name):
    raw_data = make_raw_data(data, name)
    sample_std = raw_data.std()
    sample_mean = raw_data.mean()
    sample_count = len(raw_data)
    return sample_std, sample_mean, sample_count


def create_pdf(pdf_table, name):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("tight")
    ax.axis("off")
    # pdf_table = nerdle_output
    the_table = ax.table(
        cellText=pdf_table.values,
        colLabels=pdf_table.columns,
        # colColours=["b"],
        loc="center",
    )
    pp = PdfPages(myPath + name)
    pp.savefig(fig, bbox_inches="tight")
    pp.close()
    return


### read data from csv file
data = pd.read_csv(myPath + myCSV_File, sep=",")
print(data)
list_names = data.columns.values.tolist()
if "Bin" in list_names:
    try:
        list_names.remove("Bin")
    except:
        pass

### get names
### name1 = list_names[0]
###
### for name2 in list_names[1:]:
###     get_KSstats(data, name1, name2)


### myStats3 = stats.kstest(raw_data1, raw_data2)
### print(myStats3)

nerdle_output = create_output(list_names)

for name1 in list_names:
    for name2 in list_names:
        if name1 != name2:
            pVal = get_KSstats(data, name1, name2)
            nerdle_output.at[name1, name2] = pVal
            # nerdle_output.at[name1, name1] = 1
print(nerdle_output)

nerdle_output.to_csv(myPath + "nerdle_output_pairwise.csv")
nerdle_output.to_excel(myPath + "nerdle_output_pairwise.xlsx")

nerdle_output_totals = pd.DataFrame(columns=list_names)
nerdle_output_totals.insert(
    0, "Stat", ["total played", "mean score", "st. dev.", "p-value"]
)

for name1 in list_names:
    pVal = get_KSstats_totals(data, name1)
    st_dev, mean, total = get_mean_sd(data, name1)
    nerdle_output_totals.at[0, name1] = total
    nerdle_output_totals.at[1, name1] = round(mean, 4)
    nerdle_output_totals.at[2, name1] = round(st_dev, 4)
    nerdle_output_totals.at[3, name1] = round(pVal, 4)

#  could put in here mean for all others

print(nerdle_output_totals)

nerdle_output_totals.to_csv(myPath + "nerdle_output_turkheimer.csv")
nerdle_output_totals.to_excel(myPath + "nerdle_output_turkheimer.xlsx", index=False)

pdf_table = nerdle_output
create_pdf(pdf_table, "nerdlestats1.pdf")

pdf_table = nerdle_output_totals
create_pdf(pdf_table, "nerdlestats2.pdf")

print("All done")
