import numpy as np
import pandas as pd
from datetime import datetime


def csv_to_dict(f):
    df = pd.read_csv(f)
    df = df.replace(np.nan, 0)
    data_list = []
    cols = int(df.shape[0])
    dict = {}
    int_vals = [
        "donor_score",
        "donations_this_year",
        "donations_last_year",
        "major_gift_donor",
        "major_gift_amount",
        "total_donations",
        "total_transactions",
        "total_volunteering",
    ]
    while cols:
        if not cols:
            break
        for column in df.keys():
            curr_data = df[column]
            if column == "joined_on":
                dict[column] = datetime.now()
            elif column in int_vals:
                dict[column] = (
                    int(curr_data[cols - 1]) if curr_data.get(cols - 1) else None
                )
            else:
                dict[column] = (
                    curr_data.get(cols - 1) if curr_data.get(cols - 1) else None
                )
        cols -= 1
        data_list.append(dict)
        return data_list
