import numpy as np
import typing
import pandas as pd

def labelConv32bitTo16bit(img32: np.ndarray) -> (typing.List[np.ndarray], pd.DataFrame):
    """
    Converts a 32bit image to a set of 16bit images of least possible size and returns a mapping between labels of
    input and output images
    :param img32: np.ndarray of dtype np.uint32, input 32bit image
    :return: (img16List, LabelMapDF)
    img16List: list of np.ndarray objects of dtype np.uint16, list of output 16bit images
    LabelMapDF: pandas.DataFrame, with the columns "Input Label", "Output Image index", "Output Label"
    """

    assert type(img32) is np.ndarray, "Argument img32 needs to be of type numpy.ndarray"
    assert img32.dtype == np.uint32, "Argument img32 needs to have dtype numpy.uint32"

    maxLabel = img32.max()
    nLabelsImg16 = 2 ** 16 - 1
    nOutImages = int(np.ceil(maxLabel / nLabelsImg16))

    labelMapDF = pd.DataFrame()
    img16List = []

    ipLabels = np.unique(img32)
    ipLabels = ipLabels[ipLabels != 0]

    for outImageInd in range(nOutImages):

        # print(f"Doing image {outImageInd + 1}")
        opStart = 1
        ipStart = 1 + outImageInd * nLabelsImg16

        labelMapFunc, ipEnd = getIntegerShiftWindowFunc(nLabelsImg16, ipStart, opStart)

        outImage32 = labelMapFunc(img32)

        assert np.logical_and(outImage32 >= 0, outImage32 < 2**16).all(), \
            "There is a problem with tranlating image pixel values to 16bit"

        outImage16 = outImage32.astype(np.uint16)

        img16List.append(outImage16)

        currentLabelMap = pd.DataFrame()
        currentRetainedIPLabels = ipLabels[np.logical_and(ipLabels >= ipStart, ipLabels <= ipEnd)]
        currentLabelMap["Input Label"] = currentRetainedIPLabels
        currentLabelMap["Output Image Index"] = outImageInd
        currentLabelMap["Output Label"] = labelMapFunc(currentRetainedIPLabels)
        labelMapDF = labelMapDF.append(currentLabelMap, ignore_index=True)

    return img16List, labelMapDF


def getIntegerShiftWindowFunc(nLabels2Retain: int, inputStart: int, outputStart: int) -> (typing.Callable, int):
    """
    Creates an returns a vectorized function that sequentially applies the following to its input:
    (i) subtraction of (<inputStart> - <outputStart>) and
    (ii) setting all values outside [<outputStart>, <outputStart> + nLabels2Retain -1]
    :param nLabels2Retain: int, number of labels to retain
    :param inputStart: int, lowest integer that is to be retained in the input of created function
    :param outputStart: int, lowest integer in the output of created function
    :return: (vecF, ipLast)
    vecF: vectorized function
    ipLast: Maximum value in the input of <vecF> that is retained
    """

    def f(x):
        y = x - (inputStart - outputStart)
        y = y if outputStart <= y <= outputStart + nLabels2Retain - 1 else 0
        return y

    ipLast = inputStart + nLabels2Retain - 1

    return np.vectorize(f), ipLast

