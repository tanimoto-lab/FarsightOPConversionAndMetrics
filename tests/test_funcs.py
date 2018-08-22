from FarsightOPConv.core import FarsighOutputConverter
from FarsightOPConv.app.coreFunction import farsightOPConvAndMetrics
import logging
import pandas as pd
import numpy as np
from FarsightOPConv.tifffile import imread
import os



def test_getDesiredLabelDF():
    """
    Testing the function FarsightOPConv.funcs.getDesiredLabelsDF
    :return:
    """
    testLabelFile = "tests/files/Act5C_no5_med1_C428_dec1_label.tif"
    testSeedsFile = "tests/files/Act5C_no5_med1_C428_dec1_seedPoints.txt"

    expectedXL = "tests/files/funcs/getDesiredLabelDF/expectedOP.xlsx"

    foc = FarsighOutputConverter(testLabelFile, testSeedsFile)
    desiredLabelDF = foc.getDesiredLabelsDF()

    desiredLabelDF.to_excel(expectedXL)

    assert False


def test_getLabelSeparability():
    """
    Testing the function FarsightOPConv.funcs.getLabelSeparability
    :return:
    """

    testLabelFile = "tests/files/Act5C_no5_med1_C428_dec1_label.tif"
    testSeedsFile = "tests/files/Act5C_no5_med1_C428_dec1_seedPoints.txt"

    foc = FarsighOutputConverter(testLabelFile, testSeedsFile)
    logging.info("Getting current labels and desired labels....")
    desiredLabelDF = foc.getDesiredLabelsDF()

    expectedOPXL = "tests/files/funcs/getLabelSeparability/expectedOP.xlsx"

    expectedOPDF = pd.DataFrame()
    logging.info("Calculating Label separability....")
    for currentFarsightLabel, cflDF in desiredLabelDF.groupby("Farsight Output Label"):

        print(f"Doing Farsight OP label {currentFarsightLabel}")
        seeds = cflDF.iloc[:, :3].values

        separabilities, separatedLabels = foc.getLabelSeparability(currentFarsightLabel, seeds)

        cflDF["Separability"] = separabilities
        cflDF["Intermediate Label During Separation"] = separatedLabels

        expectedOPDF = expectedOPDF.append(cflDF, ignore_index=True)

    expectedOPDF.to_excel(expectedOPXL)

    assert False


def test_separateMultipleLabels():
    """
    Testing the method FarsightOPConv.core.separateMultipleLabels
    """

    testLabelFile = "tests/files/funcs/separateMultipleLabels/Act5C_no5_med1_C428_dec1_label_20LabelSubset.tiff"
    testSeedsFile = "tests/files/funcs/separateMultipleLabels/Act5C_no5_med1_C428_dec1_seedPoints_20LabelSubset.txt"

    foc = FarsighOutputConverter(testLabelFile, testSeedsFile)

    relabelledImage, newOldLabelMap = foc.separateMultipleLabels()

    df = pd.DataFrame()
    df["oldlabels"] = newOldLabelMap.values()
    df["newLabels"] = newOldLabelMap.keys()

    successes = []
    diffPixels = []
    for oldLabel, oldLabelDF in df.groupby("oldlabels"):

        oldLabelPixelsMap = foc.labelImage == oldLabel

        newLabelPixels = np.zeros_like(relabelledImage, dtype=bool)
        for newLabel in oldLabelDF["newLabels"]:
            newLabelPixels = np.logical_or(newLabelPixels, relabelledImage == newLabel)

        successes.append(np.allclose(oldLabelPixelsMap, newLabelPixels))
        diffPixels.append((oldLabelPixelsMap != newLabelPixels).sum())

        print(f"OldLabel={oldLabel}, success={successes[-1]}, diff={diffPixels[-1]}")

    assert all(successes)


def test_getLabelSubsetImage():
    """Testing the function FarsightOPConv.core.getLabelSubsetImage"""

    testLabelFile = "tests/files/Act5C_no5_med1_C428_dec1_label.tif"
    testSeedsFile = "tests/files/Act5C_no5_med1_C428_dec1_seedPoints.txt"


    foc = FarsighOutputConverter(testLabelFile, testSeedsFile)

    subsetLabels = np.random.randint(1, int(2**16 - 1), (20,))


    subsetLabelImage, subsetSeeds = foc.getLabelSubsetImage(subsetLabels)

    for subsetLabel in subsetLabels:

        oldImageInds = np.where(foc.labelImage == subsetLabel)
        newImageInds = np.where(foc.labelImage == subsetLabel)

        assert np.allclose(oldImageInds, newImageInds)

    temp = set(np.unique(subsetLabelImage))
    temp.remove(0)
    assert temp == set(subsetLabels)


def test_coreFunction():
    """
    Testing FarsighOPConv.app.coreFunction
    """

    testLabelFile = os.path.join("tests", "files", "funcs", "coreFunction",
                                 "Act5C_no5_med1_C428_dec1_label_20LabelSubset.tiff")
    testSeedsFile = os.path.join("tests", "files", "funcs", "coreFunction",
                                 "Act5C_no5_med1_C428_dec1_seedPoints_20LabelSubset.txt")

    expOutLabelFile = os.path.join("tests", "files", "funcs", "coreFunction",
                      "Act5C_no5_med1_C428_dec1_label_20LabelSubset_corrected32Bit_exp.tiff")
    expOutXLFile = os.path.join("tests", "files", "funcs", "coreFunction",
                   "Act5C_no5_med1_C428_dec1_label_20LabelSubset_corrected32Bit_exp.xlsx")

    # testLabelFile = "tests/files/Act5C_no5_med1_C428_dec1_label.tif"
    # testSeedsFile = "tests/files/Act5C_no5_med1_C428_dec1_seedPoints.txt"

    outLabelFile, outXLFile = farsightOPConvAndMetrics(testLabelFile, testSeedsFile)

    assert np.allclose(imread(outLabelFile), imread(expOutLabelFile))

    assert pd.read_excel(outXLFile).equals(pd.read_excel(expOutXLFile))


if __name__ == "__main__":
    test_coreFunction()



