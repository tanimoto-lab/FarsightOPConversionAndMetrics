from FarsightOPConv.core import FarsighOutputConverter
from FarsightOPConv.app.coreFunction import farsightOPConvAndMetrics
from FarsightOPConv.sitkFuncs import getLabelShapeStatistics
from FarsightOPConv.img32bit16bitIO import labelConv32bitTo16bit
import logging
import pandas as pd
import numpy as np
from FarsightOPConv import tifffile
import os
import time
import SimpleITK as sitk
from ast import literal_eval as make_tuple

def test_separateMultipleLabels():
    """
    Testing the method FarsightOPConv.core.separateMultipleLabels
    """

    testLabelFile = "tests/files/Act5C_no5_med1_C428_dec1_label_20LabelSubset.tif"
    testSeedsFile = "tests/files/Act5C_no5_med1_C428_dec1_seedPoints_20LabelSubset.txt"

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


def test_coreFunction_small():
    """
    Testing FarsighOPConv.app.coreFunction with a short runtime case
    """

    testLabelFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_label_20LabelSubset.tif")
    testSeedsFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_seedPoints_20LabelSubset.txt")

    expOutLabelFile = os.path.join("tests", "files",
                      "Act5C_no5_med1_C428_dec1_label_20LabelSubset_corrected32Bit_exp.tiff")
    expOutXLFile = os.path.join("tests", "files",
                   "Act5C_no5_med1_C428_dec1_label_20LabelSubset_corrected32Bit_exp.xlsx")


    print(f"Running tests using\n{testLabelFile} and\n{testSeedsFile}")
    startTime = time.time()
    outLabelFile, outXLFile = farsightOPConvAndMetrics(testLabelFile, testSeedsFile)
    endTime = time.time()

    duration = endTime - startTime

    print(f"Execution time of core Function: {duration/60}min")

    assert np.allclose(tifffile.imread(outLabelFile), tifffile.imread(expOutLabelFile))

    assert pd.read_excel(outXLFile).equals(pd.read_excel(expOutXLFile))


def test_coreFunction_medium():
    """
    Testing FarsighOPConv.app.coreFunction with a medium runtime case
    """

    testLabelFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_label_6630LabelSubset.tif")
    testSeedsFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_seedPoints_6630LabelSubset.txt")



    expOutLabelFile = os.path.join("tests", "files",
                      "Act5C_no5_med1_C428_dec1_label_6630LabelSubset_corrected32Bit_exp.tif")
    expOutXLFile = os.path.join("tests", "files",
                   "Act5C_no5_med1_C428_dec1_label_6630LabelSubset_corrected32Bit_exp.xlsx")


    print(f"Running tests using\n{testLabelFile} and\n{testSeedsFile}")
    startTime = time.time()
    outLabelFile, outXLFile = farsightOPConvAndMetrics(testLabelFile, testSeedsFile)
    endTime = time.time()

    duration = endTime - startTime

    print(f"Execution time of core Function: {duration/60}min")

    assert np.allclose(tifffile.imread(outLabelFile), tifffile.imread(expOutLabelFile))

    assert pd.read_excel(outXLFile).equals(pd.read_excel(expOutXLFile))


def test_coreFunction_long():
    """
    Testing FarsighOPConv.app.coreFunction with a long runtime case
    """

    testLabelFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_label.tif")
    testSeedsFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_seedPoints.txt")



    expOutLabelFile = os.path.join("tests", "files",
                      "Act5C_no5_med1_C428_dec1_label_corrected32Bit_exp.tif")
    expOutXLFile = os.path.join("tests", "files",
                   "Act5C_no5_med1_C428_dec1_label_corrected32Bit_exp.xlsx")


    print(f"Running tests using\n{testLabelFile} and\n{testSeedsFile}")
    startTime = time.time()
    outLabelFile, outXLFile = farsightOPConvAndMetrics(testLabelFile, testSeedsFile)
    endTime = time.time()

    duration = endTime - startTime

    print(f"Execution time of core Function: {duration/60}min")

    assert np.allclose(tifffile.imread(outLabelFile), tifffile.imread(expOutLabelFile))

    assert pd.read_excel(outXLFile).equals(pd.read_excel(expOutXLFile))


def test_getLabelShapeStats():
    """
    Testing the function FarsightOPConv.sitkFuncs.getLabelShapeStatistics
    """

    testFile = os.path.join("tests", "files",
                                 "Act5C_no5_med1_C428_dec1_label_20LabelSubset_corrected32Bit_exp.tiff")
    outFile = os.path.join("tests", "files", "funcs", "getLabelShapeStats", "output.xlsx")
    expected_outFile = os.path.join("tests", "files", "funcs", "getLabelShapeStats", "expectedOutput.xlsx")

    testImageNP = tifffile.imread(testFile)
    testImageNPUInt16 = testImageNP.astype(np.uint16)

    measureNames, measureValues = getLabelShapeStatistics(testImageNPUInt16)

    outDF = pd.DataFrame(columns=measureNames, data=measureValues)
    outDF.to_excel(outFile)

    expected_outDF = pd.read_excel(expected_outFile)

    arrayCols = ["Centroid", "Principal Moments"]

    expected_outDF[arrayCols] = expected_outDF[arrayCols].applymap(make_tuple)

    assert outDF.equals(expected_outDF)


def test_labelConv32bitTo16bit():
    """
    Testing the function FarsightOPConv.img32bit16bitIO.labelConv32bitTo16bit
    """

    test32BitFile = os.path.join("tests", "files", "Act5C_no5_med1_C428_dec1_label_corrected32Bit_13LabelSubset.tif")

    img32bit = tifffile.imread(test32BitFile)

    imgs16Bit, labelMap = labelConv32bitTo16bit(img32bit)

    assert len(imgs16Bit) == 3

    opImgBase = os.path.join("tests", "files", "funcs", "labelConv32bitTo16bit", "outputImg")

    expOPImageFiles = [f"{opImgBase}_{ind:d}_exp.tif" for ind in range(3)]
    expLabelMapXL = os.path.join("tests", "files", "funcs", "labelConv32bitTo16bit", "outputLabelMap_exp.xlsx")
    expLabelMapDF = pd.read_excel(expLabelMapXL)

    assert expLabelMapDF.equals(labelMap.astype(np.int64))

    for expOPImageFile, opImg in zip(expOPImageFiles, imgs16Bit):

        expOPImage = tifffile.imread(expOPImageFile)
        assert np.allclose(expOPImage, opImg)


if __name__ == "__main__":
    test_coreFunction_medium()
    np.logical_or


