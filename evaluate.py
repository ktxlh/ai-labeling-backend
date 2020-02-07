import json
import os
import sys


##
# Usage: python evaluate.py [Ground Truth Dir] [Candidate Dir]
#
# It compares each file in candidate directory to the ground truth.
#   Then adds 1 point if they are identical, subtracts 3 points otherwise.
#   At the end prints the score to STDOUT.

def parse_argv(argv_list):
    if len(argv_list) != 3:
        raise Exception(
            "Wrong arguments length\n\
            Usage: python evauluate.py [Ground Truth Dir Path]\
            [Candidate Dir Path]")
    if not os.path.isdir(argv_list[1]) or not os.path.isdir(argv_list[2]):
        raise Exception("Either arguments is not a directory path\n\
            Usage: python evauluate.py [Ground Truth Dir Path]\
            [Candidate Dir Path]")

    return argv_list[1], argv_list[2]


def is_identical(ground_truth_file, candidate_file):
    if not os.path.isfile(ground_truth_file):
        return False

    gt = json.load(open(ground_truth_file))
    try:
        cand = json.load(open(candidate_file))
    except json.decoder.JSONDecodeError:
        return False

    if not cand.__contains__("text") or gt["text"] != cand["text"]:
        return False

    if not cand.__contains__("elements"):
        return False

    for elem in cand["elements"]:
        if not elem.__contains__("boundingBox"):
            return False

    gt_elements = map(lambda x: tuple(x["boundingBox"]), gt["elements"])
    cand_elements = map(lambda x: tuple(x["boundingBox"]), cand["elements"])

    return set(gt_elements) == set(cand_elements)


def score(correct, wrong):
    if not isinstance(correct, int) or not isinstance(wrong, int):
        raise TypeError("Arguments for score are not integer")

    return correct * 1 + wrong * (-3)


def main():
    ground_truth_dir, candidate_dir = parse_argv(sys.argv)

    correct = 0
    wrong = 0
    for f in os.listdir(candidate_dir):
        if os.path.isfile(os.path.join(candidate_dir, f)):
            ground_truth_file = os.path.join(ground_truth_dir, f)
            candidate_file = os.path.join(candidate_dir, f)

            if is_identical(ground_truth_file, candidate_file):
                correct += 1
            else:
                wrong += 1

    return score(correct, wrong)


print(main())
