import pandas as pd
import numpy as np
from skimage import measure
from FarsightOPConv import tifffile
import logging
import typing


class FarsighOutputConverter(object):

    def __init__(self, outputlabelImageFile:str, outputSeedsTXT: str):
        """
        Initializes the object by reading in output label image and seeds
        :param outputLabelImageFile: string, path of the output label image file generated by farsight
        :param outputSeedsTXT: string, path of the output seed text file generated by farsight
        """

        self.outputlabelImageFile = outputlabelImageFile
        self.outputSeedsTXT = outputSeedsTXT

        self.seeds = np.loadtxt(self.outputSeedsTXT, dtype=int)
        self.labelImage = tifffile.imread(self.outputlabelImageFile)


    def getDesiredLabelsDF(self):
        """
        From the output label image (<outputLabelImage>) and output seeds (<outputSeedsTXT>) of Farsight,
        creates and returns a pandas data frame with the columns "Seed", "Farsight Output Label" and
        "Desired Replacement Label". The desired label is one larger than the line number of the corresponding seed in
        <outputSeedsTXT>
        :return: pd.DataFrame
        """


        opCols = ["Seed X\n(pixels)",
                  "Seed Y\n(pixels)",
                  "Seed Z\n(pixels)",
                  "Farsight Output Label",
                  "Desired Replacement Label"]

        opList = []
        for ind, (x, y, z) in enumerate(self.seeds):

            currLabel = self.labelImage[z, y, x]

            if currLabel > 0:
                opList.append((x, y, z, currLabel, ind + 1))

        opDF = pd.DataFrame(data=opList, columns=opCols)
        return opDF

    def getLabelSeparability(self, currentFarsightLabel: int, outputSeeds: typing.List[int]):
        """
        Calculates if the seeds associated with a farsight label are separable, i.e., whether the seeds are part of separable
        connected components.
        :param currentFarsightLabel: int, farsight label
        :param outputSeeds: list of seeds, where each seed is a 3 member iterable of ints
        :return: (separability, separatedLabel)
        separability: list of bools, having the same size as <outputSeeeds>, indicating the separability of the seeds
        separatedLabel: list of ints, labels assigned to the seeds after separation
        """

        labelMaskImage = np.array(self.labelImage == currentFarsightLabel, dtype=int)

        assert labelMaskImage.sum() > 0, f"Label {currentFarsightLabel} not found in label image!"

        separatedLabelImage = measure.label(labelMaskImage, background=0, connectivity=2)

        separatedSeedLabels = [separatedLabelImage[z, y, x] for x, y, z in outputSeeds]

        separationDict = {}
        separability = []

        for ind, label in enumerate(separatedSeedLabels):

            if label in separationDict:
                separationDict[label].append(outputSeeds[ind])
                separability.append(False)
            else:
                separationDict[label] = [outputSeeds[ind]]
                separability.append(True)

        return separability, separatedSeedLabels

    def separateMultipleLabels(self):
        """
        Identify and separately label connected components in self.labelImage. A connected component here is a set of
        voxels with the same pixel value and laterally or diagonally connected.
        :return: (relabelledImage, newOldLabelMap)
        relabelledImage: numpy.ndarray of the same size as self.labelImage, with labels changed
        oldLabelnewLabelDict: dict, with old labels as keys and new labels as values. If an old label has no
        corresponding new label, the new label with be none
        """

        relabelledImage = measure.label(self.labelImage, connectivity=2)

        newOldLabelMap = {relabelledImage[z, y, x]: self.labelImage[z, y, x] for x, y, z in self.seeds}

        return relabelledImage, newOldLabelMap

    def getLabelSubsetImage(self, labelSubset: typing.Tuple[int]):
        """
        Returns a copy of  self.labelImage> with pixels with labels not in <labelSubset> set to zero.
        A corresponding subset of self.seeds is also formed and returned

        :param labelSubset: tuple of ints
        :return: (subsetLabelImage, subsetSeeds)
        subsetLabelImage: numpy.ndarray of the same shape as labelImage
        subsetSeeds: tuple of numpy.ndarrays of size (3,)
        """

        subsetLabelImage = np.zeros_like(self.labelImage)

        labelUnique = np.unique(self.labelImage)

        for label in labelSubset:
            assert label in labelUnique
            subsetLabelImage[self.labelImage == label] = label

        subsetSeeds = tuple(x for x in self.seeds if subsetLabelImage[x[2], x[1], x[0]] > 0)

        return subsetLabelImage, subsetSeeds


def replaceLabels(image: np.ndarray, labels2Replace:typing.Iterable, replaceValue, makeGenerator=False) -> np.ndarray:
    """
    Replaces the values of pixels in <labels2Replace> with replaceValue
    :param image: np.ndarray, input image
    :param toReplace: iterable of labels, of the type image.dtype
    :param replaceValue: value of type image.dtype
    :return: np.ndarray
    """

    imageCopy = image.copy()

    assert all(type(x) == image.dtype for x in labels2Replace), \
        f"All elements of labels2Replace are not of type {image.dype}"

    toRemoveMask = np.zeros_like(image, dtype=bool)
    if makeGenerator:

        for ind, labels2Replace in enumerate(labels2Replace):
            yield 0
            toRemoveMask = np.logical_or(toRemoveMask, image == labels2Replace)

    else:

        for ind, labels2Replace in enumerate(labels2Replace):
            toRemoveMask = np.logical_or(toRemoveMask, image == labels2Replace)

    imageCopy[toRemoveMask] = replaceValue

    if makeGenerator:
        yield imageCopy
    else:
        return imageCopy


