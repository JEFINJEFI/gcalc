from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}
GRP2_PARAMS = {
    "MNL2":  {"rebate_rate": 0.0049, "od_rate": 0.0096, "od_inc_days": 270},
    "MNL3":  {"rebate_rate": 0.0099, "od_rate": 0.0096, "od_inc_days": 270},
    "MNL11": {"rebate_rate": 0.0199, "od_rate": 0.0096, "od_inc_days": 365},
    "MNL20": {"rebate_rate": 0.0099, "od_rate": 0.0096, "od_inc_days": 365},
    "MSP01": {"rebate_rate": 0.0599, "od_rate": 0.0021, "od_inc_days": 270},
    "MSP02": {"rebate_rate": 0.0899, "od_rate": 0.0021, "od_inc_days": 270},
    "MSP05": {"rebate_rate": 0.0599, "od_rate": 0.0301, "od_inc_days": 270},
    "MSP06": {"rebate_rate": 0.0899, "od_rate": 0.0321, "od_inc_days": 360}
}

GRP3_PARAMS = {
    "MNL5":  {"rebate_1": 0.0709, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270},
    "MNL10": {"rebate_1": 0.0824, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270},
    "MNL12": {"rebate_1": 0.0899, "rebate_2": 0.0099, "od_rate": 0.0096, "od_inc_days": 365},
    "MNL21": {"rebate_1": 0.0699, "rebate_2": 0.0099, "od_rate": 0.0096, "od_inc_days": 365},
    "MTP5":  {"rebate_1": 0.0499, "rebate_2": 0.0199, "od_rate": 0.0096, "od_inc_days": 270},
    "MTP10": {"rebate_1": 0.0699, "rebate_2": 0.0199, "od_rate": 0.0096, "od_inc_days": 270},
    "MTP20": {"rebate_1": 0.0899, "rebate_2": 0.0199, "od_rate": 0.0096, "od_inc_days": 270},
    "MSP03": {"rebate_1": 0.0604, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270},
    "MSP04": {"rebate_1": 0.0904, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270}
}

GRP_4PARAMS = {
    "MNB01": {"rebate_1": 0.0299, "rebate_2": 0.0199, "rebate_3": 0.0099, "od_rate": 0.03, "od_inc_days": 270},
    "MNB02": {"rebate_1": 0.0399, "rebate_2": 0.0299, "rebate_3": 0.0099, "od_rate": 0.03, "od_inc_days": 270},
    "MNB03": {"rebate_1": 0.0599, "rebate_2": 0.0399, "rebate_3": 0.0099, "od_rate": 0.03, "od_inc_days": 270},
    "MNB04": {"rebate_1": 0.1004, "rebate_2": 0.0299, "rebate_3": 0.029, "od_rate": 0.03, "od_inc_days": 270}
}

GRP_5PARAMS ={
    "MQP02": {"rebate_1": 0.0709, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270},
    "MQP03": {"rebate_1": 0.0899, "rebate_2": 0.0299, "od_rate": 0.0301, "od_inc_days": 270},
    
}

SCHEME_RATES = {
    "MNL1": {"int_rate": 0.20, "sc_rate": 0.0099, "od_rate": 0.0301, "rebate_rate": 0.0}
}

for key in GRP2_PARAMS.keys():
    SCHEME_RATES[key] = {"int_rate": 0.20, "sc_rate": 0.0099}

for key in GRP3_PARAMS.keys():
    SCHEME_RATES[key] = {"int_rate": 0.20, "sc_rate": 0.0099}

for key in GRP_4PARAMS.keys():
    SCHEME_RATES[key] = {"int_rate": 0.20, "sc_rate": 0.0099}

for key in GRP_5PARAMS.keys():
    SCHEME_RATES[key] = {"int_rate": 0.20, "sc_rate": 0.0099}


class RowData(BaseModel):
    Date: str
    ad_Charges: float
    Credit: float

class CalculateRequest(BaseModel):
    scheme: str
    pledge_value: float
    pledge_date: str
    input_df: List[RowData]



def calculate_pledge_values(scheme, pledge_value, dates_input, add_charges_input, credits_input):
    scheme = str(scheme).strip().upper()

    if scheme not in SCHEME_RATES:
        return {"error": f"Error: Scheme '{scheme}' is not recognized."}

    try:
        pledge_value = float(pledge_value)
    except (ValueError, TypeError):
        return {"error": "Error: Invalid pledge value. Please enter a number."}

    try:
        date_strs = [d.strip() for d in str(dates_input).split(',') if d.strip()]
        dates = [datetime.strptime(d, "%d/%m/%Y") for d in date_strs]
    except ValueError:
        return {"error": "Error: Invalid date format. Please ensure all dates are dd/mm/yyyy."}

    if len(dates) < 2:
        return {"error": "Error: Please enter at least one intervals date in the table."}

    try:
        add_charges_input = "0" if not add_charges_input else str(add_charges_input)
        add_charges_strs = [d.strip() for d in add_charges_input.split(',') if d.strip()]
        add_charges = [float(d) for d in add_charges_strs]
    except ValueError:
        return {"error": "Error: Invalid Additional Charges format. Please enter numbers separated by commas."}

    try:
        credits_input = "0" if not credits_input else str(credits_input)
        credits_strs = [d.strip() for d in credits_input.split(',') if d.strip()]
        credits = [float(d) for d in credits_strs]
    except ValueError:
        return {"error": "Error: Invalid Credit Amounts format. Please enter numbers separated by commas."}

    num_periods = len(dates) - 1

    if len(add_charges) < num_periods:
        add_charges += [0.0] * (num_periods - len(add_charges))
    if len(credits) < num_periods:
        credits += [0.0] * (num_periods - len(credits))

    rates = SCHEME_RATES[scheme]
    int_rate = rates["int_rate"]
    sc_rate = rates["sc_rate"]
    results = []
    
    
    if scheme == "MNL1":
        od_rate = rates["od_rate"]
        rebate_rate = rates["rebate_rate"]
        accumulated_int = 0
        accumulated_sc_total = 0
        accumulated_od_total = 0
        accumulated_rebate = 0
        accumulated_add_charges = 0
        accumulated_credits = 0

        for i in range(len(dates) - 1):
            opening_balance= pledge_value+accumulated_int+accumulated_sc_total+accumulated_od_total+accumulated_add_charges-accumulated_rebate-accumulated_credits
            d1 = dates[i]
            d2 = dates[i+1]
            diff = (d2 - d1).days

            if i == 0:
                diff += 1

            if rebate_rate > 0:
                current_principal = pledge_value + accumulated_int - accumulated_rebate + accumulated_add_charges - accumulated_credits
            else:
                total_dues = accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges
                excess_credit = max(0, accumulated_credits - total_dues)
                unpaid_add_charges = max(0, accumulated_add_charges - accumulated_credits)
                current_principal = pledge_value + unpaid_add_charges - excess_credit

            remaining_days = diff
            running_principal = current_principal
            total_int_unrounded = 0.0
            total_sc_unrounded = 0.0
            total_od_unrounded = 0.0
            split_index = 0
            current_od_rate = od_rate
            if diff > 270:
                current_od_rate += 0.02

            while remaining_days > 0:
                days_to_process = min(remaining_days, 30)
                split_int = (running_principal * int_rate * days_to_process) / 360.0
                split_sc = (current_principal * sc_rate * days_to_process) / 360.0
                split_od = 0.0

                if split_index > 0:
                    split_od = (running_principal * current_od_rate * days_to_process) / 360.0

                total_int_unrounded += split_int
                total_sc_unrounded += split_sc
                total_od_unrounded += split_od

                running_principal += (split_int + split_od)
                remaining_days -= days_to_process
                split_index += 1

            total_int = round(total_int_unrounded)
            total_sc = round(total_sc_unrounded)
            total_od = round(total_od_unrounded)

            if diff <= 30:
                total_od = 0

            rebate_val = 0
            if rebate_rate > 0 and diff <= 30:
                rebate_val = round((current_principal * rebate_rate * diff) / 360.0)
                total_int -= rebate_val
                accumulated_rebate += rebate_val

            current_add_charge = add_charges[i]
            current_credit = credits[i]
            
            closing_balance= opening_balance+accumulated_int+accumulated_sc_total+accumulated_od_total+accumulated_add_charges-accumulated_rebate-accumulated_credits
            period_result = {
                "Date": d2.strftime("%d/%m/%Y"),
                "opening_balance": round(opening_balance),
                "Interest": total_int,
                "Service Charge": total_sc,
                "Overdue": total_od,
                "Additional Charge": current_add_charge,
                "Credit Amount": current_credit,
                "closing_balance":round(closing_balance)
            }
            if rebate_rate > 0:
                period_result["Rebate"] = rebate_val
            period_result["opening balance"]= round(opening_balance)
            period_result["closing balance"]= round(closing_balance)
           
            results.append(period_result)

            accumulated_int += (total_int + rebate_val)
            accumulated_sc_total += total_sc
            accumulated_od_total += total_od
            accumulated_add_charges += current_add_charge
            accumulated_credits += current_credit

    elif scheme in GRP2_PARAMS:
        params = GRP2_PARAMS[scheme]
        rebate_rate = params["rebate_rate"]
        base_od_rate = params["od_rate"]
        od_inc_days = params["od_inc_days"]

        accumulated_int = 0
        accumulated_sc_total = 0
        accumulated_od_total = 0
        accumulated_rebate = 0
        accumulated_add_charges = 0
        accumulated_credits = 0

        for i in range(len(dates) - 1):
            opening_balance= pledge_value+accumulated_int+accumulated_sc_total+accumulated_od_total+accumulated_add_charges-accumulated_rebate-accumulated_credits
            d1 = dates[i]
            d2 = dates[i+1]
            
            diff = (d2 - d1).days

            if i == 0:
                diff += 1

            total_dues = accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges - accumulated_rebate
            excess_credit = max(0, accumulated_credits - total_dues)
            unpaid_add_charges = max(0, accumulated_add_charges - accumulated_credits)
            current_principal = pledge_value + unpaid_add_charges - excess_credit
            current_principal = max(0.0, current_principal)

            total_sc_unrounded = (current_principal * sc_rate * diff) / 360.0

            current_od_rate = base_od_rate
            if diff > od_inc_days:
                current_od_rate += 0.02

            remaining_days = diff
            running_principal = current_principal

            total_int_unrounded = 0.0
            total_od_unrounded = 0.0
            split_index = 0

            while remaining_days > 0:
                days_to_process = min(remaining_days, 30)
                split_int = (running_principal * int_rate * days_to_process) / 360.0
                split_od = 0.0

                if split_index > 0:
                    split_od = (running_principal * current_od_rate * days_to_process) / 360.0

                total_int_unrounded += split_int
                total_od_unrounded += split_od

                running_principal += (split_int + split_od)
                remaining_days -= days_to_process
                split_index += 1

            total_int = round(total_int_unrounded)
            total_sc = round(total_sc_unrounded)
            total_od = round(total_od_unrounded)
            rebate_val = 0
            if diff<= 30:
                total_od = 0
            if (d2 - d1).days == 30:
               
                V = round((current_principal * rebate_rate  * 31) / 360.0) +round((current_principal * current_od_rate * 1) / 360.0)
                rebate_val += V
                total_od = 0
            
            if diff <= 30:
                rebate_val = round((current_principal * rebate_rate * diff) / 360.0)
                accumulated_rebate += rebate_val

            current_add_charge = add_charges[i]
            current_credit = credits[i]
            if 30<(d2-d1).days <= 35:
                total_od = 0
            closing_balance=opening_balance+total_int+total_sc+total_od+current_add_charge-current_credit-rebate_val
            period_result = {
                "Date": d2.strftime("%d/%m/%Y"),
                "opening_balance": round(opening_balance),
                "Interest": total_int,
                "Service Charge": total_sc,
                "Overdue": total_od,
                "Additional Charge": current_add_charge,
                "Credit Amount": current_credit,
                "Rebate": rebate_val,
                "closing_balance": round(closing_balance)
            }
            period_result["opening balance"]= round(opening_balance)
            period_result["closing balance"]= round(closing_balance)
            results.append(period_result)

            accumulated_int += total_int
            accumulated_sc_total += total_sc
            accumulated_od_total += total_od
            accumulated_add_charges += current_add_charge
            accumulated_credits += current_credit

    elif scheme in GRP3_PARAMS:
        params = GRP3_PARAMS[scheme]
        rebate_rate_1 = params["rebate_1"]
        rebate_rate_2 = params["rebate_2"]
        base_od_rate = params["od_rate"]
        od_inc_days = params["od_inc_days"]

        accumulated_int = 0
        accumulated_sc_total = 0
        accumulated_od_total = 0
        accumulated_rebate = 0
        accumulated_add_charges = 0
        accumulated_credits = 0
        cumulative_days_before = 0

        for i in range(len(dates) - 1):
            opening_balance= pledge_value+accumulated_int+accumulated_sc_total+accumulated_od_total+accumulated_add_charges-accumulated_rebate-accumulated_credits
            d1 = dates[i]
            d2 = dates[i+1]
            
            diff = (d2 - d1).days

            if i == 0:
                diff += 1

            cumulative_days_after = cumulative_days_before + diff

            total_dues = accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges - accumulated_rebate
            excess_credit = max(0, accumulated_credits - total_dues)
            unpaid_add_charges = max(0, accumulated_add_charges - accumulated_credits)
            current_principal = pledge_value + unpaid_add_charges - excess_credit
            current_principal = max(0.0, current_principal)

            total_sc_unrounded = (current_principal * sc_rate * diff) / 360.0

            current_od_rate = base_od_rate
            if cumulative_days_after > od_inc_days:
                current_od_rate += 0.02
            
            applicable_rebate_rate = rebate_rate_1 if diff <= 33 else rebate_rate_2

            total_int_unrounded = 0.0
            total_od_unrounded = 0.0
            total_rebate_unrounded = 0.0

            if diff > 60:
                remaining_days = 60
                running_principal = current_principal
                
                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    total_int_unrounded += split_int
                    running_principal += split_int
                    remaining_days -= days_to_process
                
                extra_days = diff - 60
                
                while extra_days > 0:
                    days_to_process = min(extra_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    split_od = (running_principal * current_od_rate * days_to_process) / 360.0
                    
                    total_int_unrounded += split_int
                    total_od_unrounded += split_od
                    
                    running_principal += (split_int + split_od)
                    extra_days -= days_to_process
                
                total_rebate_unrounded = 0.0

            else:
                remaining_days = diff
                running_principal = current_principal
                split_index = 0

                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    split_rebate = (running_principal * applicable_rebate_rate * days_to_process) / 360.0
                    split_od = 0.0

                    if split_index > 0:
                        split_od = (running_principal * current_od_rate * days_to_process) / 360.0

                    total_int_unrounded += split_int
                    total_rebate_unrounded += split_rebate
                    total_od_unrounded += split_od

                    running_principal += (split_int + split_od)
                    remaining_days -= days_to_process
                    split_index += 1

            total_int = round(total_int_unrounded)
            total_sc = round(total_sc_unrounded)
            total_od = round(total_od_unrounded)
            rebate_val = round(total_rebate_unrounded)
            

            if (d2 - d1).days == 60:
                
                V = round((current_principal * rebate_rate_1  * 30) / 360.0) + round((current_principal * rebate_rate_2  * 30) / 360.0) +round((current_principal * current_od_rate * 1) / 360.0)
                rebate_val += V
                total_od = 0
            accumulated_rebate += rebate_val

            current_add_charge = add_charges[i]
            current_credit = credits[i]
            if 30<(d2-d1).days <= 35:
                total_od = 0
            closing_balance=opening_balance+total_int+total_sc+total_od+current_add_charge-current_credit-rebate_val
            period_result = {
                "Date": d2.strftime("%d/%m/%Y"),
                "opening_balance": round(opening_balance),
                "Interest": total_int,
                "Service Charge": total_sc,
                "Overdue": total_od,
                "Additional Charge": current_add_charge,
                "Credit Amount": current_credit,
                "Rebate": rebate_val,
                "closing_balance": round(closing_balance)
            }
            period_result["opening balance"]= round(opening_balance)
            period_result["closing balance"]= round(closing_balance)
            results.append(period_result)

            accumulated_int += total_int
            accumulated_sc_total += total_sc
            accumulated_od_total += total_od
            accumulated_add_charges += current_add_charge
            accumulated_credits += current_credit
            
            cumulative_days_before = cumulative_days_after
    
    




    elif scheme in GRP_4PARAMS:
        params = GRP_4PARAMS[scheme]
        rebate_rate_1 = params["rebate_1"]
        rebate_rate_2 = params["rebate_2"]
        rebate_rate_3 = params["rebate_3"]
        base_od_rate = params["od_rate"]
        od_inc_days = params["od_inc_days"]

        accumulated_int = 0
        accumulated_sc_total = 0
        accumulated_od_total = 0
        accumulated_rebate = 0
        accumulated_add_charges = 0
        accumulated_credits = 0
        cumulative_days_before = 0

        for i in range(len(dates) - 1):
            opening_balance = pledge_value + accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges - accumulated_rebate - accumulated_credits
            d1 = dates[i]
            d2 = dates[i+1]
            
            diff = (d2 - d1).days

            if i == 0:
                diff += 1

            cumulative_days_after = cumulative_days_before + diff

            total_dues = accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges - accumulated_rebate
            excess_credit = max(0, accumulated_credits - total_dues)
            unpaid_add_charges = max(0, accumulated_add_charges - accumulated_credits)
            current_principal = pledge_value + unpaid_add_charges - excess_credit
            current_principal = max(0.0, current_principal)

            total_sc_unrounded = (current_principal * sc_rate * diff) / 360.0

            current_od_rate = base_od_rate
            if cumulative_days_after > od_inc_days:
                current_od_rate += 0.03
            
           
            if diff <= 33:
                applicable_rebate_rate = rebate_rate_1
            elif 33 < diff <= 60:
                applicable_rebate_rate = rebate_rate_2
            else:
                applicable_rebate_rate = rebate_rate_3

            total_int_unrounded = 0.0
            total_od_unrounded = 0.0
            total_rebate_unrounded = 0.0

            if diff > 270:
                remaining_days = 270
                running_principal = current_principal
                
               
                split_index = 0
                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    total_int_unrounded += split_int
                    
                   
                    if split_index <= 2:
                        if split_index == 0:
                            current_step_rebate = rebate_rate_1
                        elif split_index == 1:
                            current_step_rebate = rebate_rate_2
                        else:
                            current_step_rebate = rebate_rate_3
                        split_rebate = (running_principal * current_step_rebate * days_to_process) / 360.0
                        total_rebate_unrounded += split_rebate

                    running_principal += split_int
                    remaining_days -= days_to_process
                    split_index += 1
                
                extra_days = diff - 270
                while extra_days > 0:
                    days_to_process = min(extra_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    split_od = (running_principal * current_od_rate * days_to_process) / 360.0
                    
                    total_int_unrounded += split_int
                    total_od_unrounded += split_od
                    
                    running_principal += (split_int + split_od)
                    extra_days -= days_to_process
              

            else:
                remaining_days = diff
                running_principal = current_principal
                split_index = 0

                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    
                    if split_index == 0:
                        current_step_rebate = rebate_rate_1
                    elif split_index == 1:
                        current_step_rebate = rebate_rate_2
                    else:
                        current_step_rebate = rebate_rate_3

                   
                    if split_index <= 2:
                        split_rebate = (running_principal * current_step_rebate * days_to_process) / 360.0
                    else:
                        split_rebate = 0.0
                    
                    
                    split_od = 0.0

                    total_int_unrounded += split_int
                    total_rebate_unrounded += split_rebate
                    total_od_unrounded += split_od

                    running_principal += (split_int + split_od)
                    remaining_days -= days_to_process
                    split_index += 1

            total_int = round(total_int_unrounded)
            total_sc = round(total_sc_unrounded)
            total_od = round(total_od_unrounded)
            rebate_val = round(total_rebate_unrounded)
            
            if (d2 - d1).days == 90:
                V = (round((current_principal * rebate_rate_1 * 30) / 360.0) + 
                     round((current_principal * rebate_rate_2 * 30) / 360.0) +
                     round((current_principal * rebate_rate_3 * 30) / 360.0) +
                     round((current_principal * current_od_rate * 1) / 360.0))
                rebate_val += V
                total_od = 0

            accumulated_rebate += rebate_val

            current_add_charge = add_charges[i]
            current_credit = credits[i]
            
            if 60 < (d2 - d1).days <= 63:
                total_od = 0

            closing_balance = opening_balance + total_int + total_sc + total_od + current_add_charge - current_credit - rebate_val
            period_result = {
                "Date": d2.strftime("%d/%m/%Y"),
                "opening_balance": round(opening_balance),
                "Interest": total_int,
                "Service Charge": total_sc,
                "Overdue": total_od,
                "Additional Charge": current_add_charge,
                "Credit Amount": current_credit,
                "Rebate": rebate_val,
                "closing_balance": round(closing_balance)
            }
            period_result["opening balance"] = round(opening_balance)
            period_result["closing balance"] = round(closing_balance)
            results.append(period_result)

            accumulated_int += total_int
            accumulated_sc_total += total_sc
            accumulated_od_total += total_od
            accumulated_add_charges += current_add_charge
            accumulated_credits += current_credit
            
            cumulative_days_before = cumulative_days_after
    


    elif scheme in GRP_5PARAMS:
        params = GRP_5PARAMS[scheme]
        rebate_rate_1 = params["rebate_1"]
        rebate_rate_2 = params["rebate_2"]
        base_od_rate = params["od_rate"]
        od_inc_days = params["od_inc_days"]

        accumulated_int = 0
        accumulated_sc_total = 0
        accumulated_od_total = 0
        accumulated_rebate = 0
        accumulated_add_charges = 0
        accumulated_credits = 0
        cumulative_days_before = 0

        for i in range(len(dates) - 1):
            opening_balance= pledge_value+accumulated_int+accumulated_sc_total+accumulated_od_total+accumulated_add_charges-accumulated_rebate-accumulated_credits
            d1 = dates[i]
            d2 = dates[i+1]
            
            diff = (d2 - d1).days

            if i == 0:
                diff += 1

            cumulative_days_after = cumulative_days_before + diff

            total_dues = accumulated_int + accumulated_sc_total + accumulated_od_total + accumulated_add_charges - accumulated_rebate
            excess_credit = max(0, accumulated_credits - total_dues)
            unpaid_add_charges = max(0, accumulated_add_charges - accumulated_credits)
            current_principal = pledge_value + unpaid_add_charges - excess_credit
            current_principal = max(0.0, current_principal)

            total_sc_unrounded = (current_principal * sc_rate * diff) / 360.0

            current_od_rate = base_od_rate
            if cumulative_days_after > od_inc_days:
                current_od_rate += 0.02
            
            applicable_rebate_rate = rebate_rate_1 if diff <= 33 else rebate_rate_2

            total_int_unrounded = 0.0
            total_od_unrounded = 0.0
            total_rebate_unrounded = 0.0

            
            if diff > 270:
                remaining_days = 270
                running_principal = current_principal
                
                split_index = 0
                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    total_int_unrounded += split_int
                    
                    
                    if split_index <= 2:
                        split_rebate = (running_principal * applicable_rebate_rate * days_to_process) / 360.0
                        total_rebate_unrounded += split_rebate
                        
                    running_principal += split_int
                    remaining_days -= days_to_process
                    split_index += 1
                
                extra_days = diff - 270
                while extra_days > 0:
                    days_to_process = min(extra_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    split_od = (running_principal * current_od_rate * days_to_process) / 360.0
                    
                    total_int_unrounded += split_int
                    total_od_unrounded += split_od
                    
                    running_principal += (split_int + split_od)
                    extra_days -= days_to_process

            else:
                remaining_days = diff
                running_principal = current_principal
                split_index = 0

                while remaining_days > 0:
                    days_to_process = min(remaining_days, 30)
                    split_int = (running_principal * int_rate * days_to_process) / 360.0
                    
                    
                    if split_index <= 2:
                        split_rebate = (running_principal * applicable_rebate_rate * days_to_process) / 360.0
                    else:
                        split_rebate = 0.0
                        
                    split_od = 0.0

                    
                    if split_index > 8:
                        split_od = (running_principal * current_od_rate * days_to_process) / 360.0

                    total_int_unrounded += split_int
                    total_rebate_unrounded += split_rebate
                    total_od_unrounded += split_od

                    running_principal += (split_int + split_od)
                    remaining_days -= days_to_process
                    split_index += 1

            total_int = round(total_int_unrounded)
            total_sc = round(total_sc_unrounded)
            total_od = round(total_od_unrounded)
            rebate_val = round(total_rebate_unrounded)
            

            if (d2 - d1).days == 60:
                V = round((current_principal * rebate_rate_1  * 30) / 360.0) + round((current_principal * rebate_rate_2  * 30) / 360.0) +round((current_principal * current_od_rate * 1) / 360.0)
                rebate_val += V
                total_od = 0
            accumulated_rebate += rebate_val

            current_add_charge = add_charges[i]
            current_credit = credits[i]
            if 30<(d2-d1).days <= 35:
                total_od = 0
            closing_balance=opening_balance+total_int+total_sc+total_od+current_add_charge-current_credit-rebate_val
            period_result = {
                "Date": d2.strftime("%d/%m/%Y"),
                "opening_balance": round(opening_balance),
                "Interest": total_int,
                "Service Charge": total_sc,
                "Overdue": total_od,
                "Additional Charge": current_add_charge,
                "Credit Amount": current_credit,
                "Rebate": rebate_val,
                "closing_balance": round(closing_balance)
            }
            period_result["opening balance"]= round(opening_balance)
            period_result["closing balance"]= round(closing_balance)
            results.append(period_result)

            accumulated_int += total_int
            accumulated_sc_total += total_sc
            accumulated_od_total += total_od
            accumulated_add_charges += current_add_charge
            accumulated_credits += current_credit
            
            cumulative_days_before = cumulative_days_after

    
    return {"message": f"Calculation successful for {scheme}.", "data": results}


@app.post("/calculate")
def api_calculate(req: CalculateRequest):
    if not req.input_df:
        raise HTTPException(status_code=400, detail="Please enter data into the table.")

    dates_list = [str(req.pledge_date).strip()]
    add_charges_list = []
    credits_list = []

   
    for row in req.input_df:
        date_val = str(row.Date).strip()
        if not date_val:
            continue
        
        dates_list.append(date_val)
        add_charges_list.append(row.ad_Charges)
        credits_list.append(row.Credit)

    dates_input_string = ", ".join(dates_list)
    add_charges_string = ", ".join(map(str, add_charges_list))
    credits_string = ", ".join(map(str, credits_list))

    result = calculate_pledge_values(
        req.scheme, 
        req.pledge_value, 
        dates_input_string, 
        add_charges_string, 
        credits_string
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result