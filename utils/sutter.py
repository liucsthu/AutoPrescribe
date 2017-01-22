import csv
from collections import defaultdict as dd
import codecs
import pickle
from utils.data import dump, load

def load_sutter():
    cnt = 0
    records = dd(lambda: dd(lambda: dd(list)))
    with codecs.open("SUTTER_ORDER_MED_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(records), line)
            cnt += 1
            x = line.strip().split("\t")
            records[x[0]][x[9]][x[1]].append(x)

    rec = dict(records)
    with open("sutter_prescription.pkl", "wb") as f_out:
        pickle.dump(rec, f_out)

    import json
    with open("sutter_prescription.json", "w") as f_ouut:
        json.dump(rec, f_out)


def get_pairs(data):
    meds = dd(list)
    for pid in data:
        for eid in data[pid]:
            for mid in data[pid][eid]:
                for med in data[pid][eid][mid]:
                    meds[eid].append((med[2], med[23]))


def get_prescription():
    meds = dd(set)
    cnt = 0
    with codecs.open("SUTTER_ORDER_MED_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(meds))
            cnt += 1
            x = line.strip().split("\t")
            meds[x[9]].add((x[2], x[12], x[13], x[-1]))


def get_encounter(eids):
    encounters = dd(list)
    cnt = 0
    with codecs.open("SUTTER_ENCOUNTER_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(encounters))
            cnt += 1
            x = line.strip().split("\t")
            encounters[x[1]].append(x[6])
    valid_encounters = {}
    for eid in eids:
        valid_encounters[eid] = encounters[eid]


def load_medication_details():
    medications = {}
    cnt = 0
    with codecs.open("SUTTER_MEDICATIONS_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(medications))
            cnt += 1
            x = line.split("\t")
            medications[x[0]] = x


def join_encounters(valid_encounters, meds, medications):
    pairs = []
    for eid in valid_encounters:
        pairs.append((valid_encounters[eid], meds[eid]))
    diag_pres = []
    for p in pairs:
        pres = []
        for med in p[1]:
            med_detail = medications[med[-1]]
            pres.append(tuple(list(med)+[med_detail[2], med_detail[3], med_detail[6], med_detail[7]]))
        diag_pres.append((p[0], pres))
    dump(pairs, "diagnosis_prescription_pairs.pkl")


def search_encounter_by_drug(diag_pres, code):
    results = []
    for p in diag_pres:
        for med in p[1]:
            if code == med[-1]:
                results.append(p)
    return results


def join_prescription(meds, medications):
    prescriptions = []
    for eid in meds:
        pres = []
        for med in meds[eid]:
            if not med[-1] in medications:
                continue
            med_detail = medications[med[-1]]
            pres.append(tuple(list(med)+[med_detail[2], med_detail[3], med_detail[6], med_detail[7]]))
        prescriptions.append(pres)
    dump(prescriptions, "prescriptions.pkl")

def search_precription_by_drug(prescriptions, code):
    results = []
    for p in prescriptions:
        for med in p:
            if code == med[-1]:
                results.append(p)
                break
    for r in results:
        diag = set()
        drug = set()
        for item in r:
            diag.add(item[0])
            drug.add(item[1])
        print(" ".join(diag))
        print("\n".join(drug))
        print("\n")
    return results


def clean_encounter(diag_pres):
    encounters = []
    for p in diag_pres:
        pres = set()
        for med in p[1]:
            pres.add(med[-1])
        encounters.append((p[0], list(pres)))
    dump(encounters, "sutter_encounters.pkl")


def load_encounter():
    encounters1 = set()
    encounters2 = set()
    cnt = 0
    with codecs.open("SUTTER_ENCOUNTER_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(encounters1))
            cnt += 1
            x = line.strip().split("\t")
            encounters1.add(x[1])
    cnt = 0
    with codecs.open("SUTTER_ORDER_MED_DETAIL_V1.tab", "r", encoding='utf-8', errors='ignore') as f_in:
        next(f_in)
        for line in f_in:
            if cnt % 100000 == 0:
                print(cnt, len(encounters2))
            cnt += 1
            x = line.strip().split("\t")
            encounters2.add(x[9])

    dump(encounters1.intersection(encounters2), "valid_encounters")


def group_encounter_by_diag(diag_pres):
    encounter_by_diag = dd(list)
    for p in diag_pres:
        pres = set()
        for med in p[1]:
            pres.add(med[-1])
        encounter_by_diag[tuple(p[0])].append(pres)


def get_encounter_level(encounters, level):
    new_encounters = []
    for enc in encounters:
        new_encounters.append((enc[0], [code[:level*2] for code in enc[1]]))
    dump(new_encounters, "sutter_encounters_%s.pkl" % level)


def gen_vocab(encounters):
    diag_vocab = {}
    drug_vocab = {}
    cnt1 = 0
    cnt2 = 0
    for p in encounters:
        for diag in p[0]:
            if not diag in diag_vocab:
                diag_vocab[diag] = cnt1
                cnt1 += 1
        for drug in p[1]:
            if not drug[:8] in drug_vocab:
                drug_vocab[drug[:8]] = cnt2
                cnt2 += 1
    dump(diag_vocab, "sutter_diag_vocab.pkl")
    dump(drug_vocab, "sutter_drug_vocab_4.pkl")