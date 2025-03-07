"""
PyQt6 First example display image

In this example, we create a simple
window in PyQt6.

Author: Yuan SUN
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QFrame, QGroupBox, QScrollArea, QLabel, QGridLayout, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt, QPoint
import pyqtgraph as pg
from cxx_image_io import read_image, PixelRepresentation, PixelType
import argparse
import pathlib
import numpy as np


class ImageDisplayer(QWidget):
    image = None
    metadata = None
    image_path = None
    frame = None
    tabWidget = None
    imagepic = None
    imageArea = None

    def __init__(self, image, metadata, image_path):
        super().__init__()
        self.image = image
        self.metadata = metadata
        self.image_path = image_path
        self.initUI()
        self.showImage()
        self.showMetadata()

    def mousePressEvent(self, event):
        position = QCursor.pos()

        x = position.x()
        y = position.y()

        label_x = self.imagepic.mapToGlobal(QPoint(0, 0)).x()
        label_y = self.imagepic.mapToGlobal(QPoint(0, 0)).y()

        pix_x = x - label_x
        pix_y = y - label_y

        pixel_value = self.image[pix_y, pix_x]
        pixel_status = "Position：x = {}, y = {}, value = {}".format(
            pix_x, pix_y, pixel_value)

        if pix_x >= 0 and pix_x < self.image.shape[
                1] and pix_y >= 0 and pix_y < self.image.shape[0]:
            self.pixelStatus.setText(pixel_status)

    def initImageViewUI(self):
        self.tabWidget = QTabWidget(self)
        self.tabImage = QWidget(self.tabWidget)
        self.tabWidget.addTab(self.tabImage, str(self.image_path))
        self.imageArea = QScrollArea(self.tabImage)
        vbox = QVBoxLayout(self.tabImage)
        vbox.addWidget(self.imageArea)
        self.imagepic = QLabel(self.imageArea)
        self.imagepic.setText('Image preview')
        self.imageArea.setWidget(self.imagepic)
        self.imageArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixelStatus = QLabel("Ready", self)
        vbox.addWidget(self.pixelStatus)

    def initFileInfoUI(self, tabFileInfo):

        labfileFormat = QLabel("fileFormat", tabFileInfo)
        self.labfileFormatValue = QLabel(tabFileInfo)
        labpixelRepresentation = QLabel("pixelRepresentation", tabFileInfo)
        self.labpixelRepresentationValue = QLabel(tabFileInfo)
        labimageLayout = QLabel("imageLayout", tabFileInfo)
        self.labimageLayoutValue = QLabel(tabFileInfo)
        labpixelType = QLabel("pixelType", tabFileInfo)
        self.labpixelTypeValue = QLabel(tabFileInfo)
        labpixelPrecision = QLabel("pixelPrecision", tabFileInfo)
        self.labpixelPrecisionValue = QLabel(tabFileInfo)
        labwidth = QLabel("width", tabFileInfo)
        self.labwidthValue = QLabel(tabFileInfo)
        labheight = QLabel("height", tabFileInfo)
        self.labheightValue = QLabel(tabFileInfo)
        labwidthAlignment = QLabel("widthAlignment", tabFileInfo)
        self.labwidthAlignmentValue = QLabel(tabFileInfo)
        labheightAlignment = QLabel("heightAlignment", tabFileInfo)
        self.labheightAlignmentValue = QLabel(tabFileInfo)
        labsizeAlignment = QLabel("sizeAlignment", tabFileInfo)
        self.labsizeAlignmentValue = QLabel(tabFileInfo)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labfileFormat, 0, 0)
        grid_layout.addWidget(self.labfileFormatValue, 0, 1)
        grid_layout.addWidget(labpixelRepresentation, 1, 0)
        grid_layout.addWidget(self.labpixelRepresentationValue, 1, 1)
        grid_layout.addWidget(labimageLayout, 2, 0)
        grid_layout.addWidget(self.labimageLayoutValue, 2, 1)
        grid_layout.addWidget(labpixelType, 3, 0)
        grid_layout.addWidget(self.labpixelTypeValue, 3, 1)
        grid_layout.addWidget(labpixelPrecision, 4, 0)
        grid_layout.addWidget(self.labpixelPrecisionValue, 4, 1)
        grid_layout.addWidget(labwidth, 5, 0)
        grid_layout.addWidget(self.labwidthValue, 5, 1)
        grid_layout.addWidget(labheight, 6, 0)
        grid_layout.addWidget(self.labheightValue, 6, 1)
        grid_layout.addWidget(labwidthAlignment, 7, 0)
        grid_layout.addWidget(self.labwidthAlignmentValue, 7, 1)
        grid_layout.addWidget(labheightAlignment, 8, 0)
        grid_layout.addWidget(self.labheightAlignmentValue, 8, 1)
        grid_layout.addWidget(labsizeAlignment, 9, 0)
        grid_layout.addWidget(self.labsizeAlignmentValue, 9, 1)

        grid_layout.setRowStretch(grid_layout.rowCount(), 1)

        tabFileInfo.setLayout(grid_layout)

    def initExifUI(self, tabExif):
        labimageWidth = QLabel("imageWidth", tabExif)
        self.labimageWidthValue = QLabel(tabExif)
        labimageHeight = QLabel("imageHeight", tabExif)
        self.labimageHeightValue = QLabel(tabExif)
        labimageDescription = QLabel("imageDescription", tabExif)
        self.labimageDescriptionValue = QLabel(tabExif)
        labmake = QLabel("make", tabExif)
        self.labmakeValue = QLabel(tabExif)
        labmodel = QLabel("model", tabExif)
        self.labmodelValue = QLabel(tabExif)
        laborientation = QLabel("orientation", tabExif)
        self.laborientationValue = QLabel(tabExif)
        labsoftware = QLabel("software", tabExif)
        self.labsoftwareValue = QLabel(tabExif)
        labexposureTime = QLabel("exposureTime", tabExif)
        self.labexposureTimeValue = QLabel(tabExif)
        labfNumber = QLabel("fNumber", tabExif)
        self.labfNumberValue = QLabel(tabExif)
        labisoSpeedRatings = QLabel("isoSpeedRatings", tabExif)
        self.labisoSpeedRatingsValue = QLabel(tabExif)
        labdateTimeOriginal = QLabel("dateTimeOriginal", tabExif)
        self.labdateTimeOriginalValue = QLabel(tabExif)
        labbrightnessValue = QLabel("brightnessValue", tabExif)
        self.labbrightnessValueValue = QLabel(tabExif)
        labexposureBiasValue = QLabel("exposureBiasValue", tabExif)
        self.labexposureBiasValueValue = QLabel(tabExif)
        labfocalLength = QLabel("focalLength", tabExif)
        self.labfocalLengthValue = QLabel(tabExif)
        labfocalLengthIn35mmFilm = QLabel("focalLengthIn35mmFilm", tabExif)
        self.labfocalLengthIn35mmFilmValue = QLabel(tabExif)

        grid_layout = QGridLayout()
        grid_layout.addWidget(labimageWidth, 0, 0)
        grid_layout.addWidget(self.labimageWidthValue, 0, 1)
        grid_layout.addWidget(labimageHeight, 1, 0)
        grid_layout.addWidget(self.labimageHeightValue, 1, 1)
        grid_layout.addWidget(labimageDescription, 2, 0)
        grid_layout.addWidget(self.labimageDescriptionValue, 2, 1)
        grid_layout.addWidget(labmake, 3, 0)
        grid_layout.addWidget(self.labmakeValue, 3, 1)
        grid_layout.addWidget(labmodel, 4, 0)
        grid_layout.addWidget(self.labmodelValue, 4, 1)
        grid_layout.addWidget(laborientation, 5, 0)
        grid_layout.addWidget(self.laborientationValue, 5, 1)
        grid_layout.addWidget(labsoftware, 6, 0)
        grid_layout.addWidget(self.labsoftwareValue, 6, 1)
        grid_layout.addWidget(labexposureTime, 7, 0)
        grid_layout.addWidget(self.labexposureTimeValue, 7, 1)
        grid_layout.addWidget(labfNumber, 8, 0)
        grid_layout.addWidget(self.labfNumberValue, 8, 1)
        grid_layout.addWidget(labisoSpeedRatings, 9, 0)
        grid_layout.addWidget(self.labisoSpeedRatingsValue, 9, 1)
        grid_layout.addWidget(labdateTimeOriginal, 10, 0)
        grid_layout.addWidget(self.labdateTimeOriginalValue, 10, 1)
        grid_layout.addWidget(labbrightnessValue, 11, 0)
        grid_layout.addWidget(self.labbrightnessValueValue, 11, 1)
        grid_layout.addWidget(labexposureBiasValue, 12, 0)
        grid_layout.addWidget(self.labexposureBiasValueValue, 12, 1)
        grid_layout.addWidget(labfocalLength, 13, 0)
        grid_layout.addWidget(self.labfocalLengthValue, 13, 1)
        grid_layout.addWidget(labfocalLengthIn35mmFilm, 14, 0)
        grid_layout.addWidget(self.labfocalLengthIn35mmFilmValue, 14, 1)
        grid_layout.setRowStretch(grid_layout.rowCount(), 1)
        tabExif.setLayout(grid_layout)

    def initMetadataUI(self):
        self.frame = QFrame(self)
        framelayout = QVBoxLayout(self.frame)
        groupbox = QGroupBox("Image Metadata", self.frame)
        grouplayout = QVBoxLayout(groupbox)

        tabWidgetMeta = QTabWidget(groupbox)
        tabExif = QWidget(tabWidgetMeta)
        tabFileInfo = QWidget(tabWidgetMeta)
        tabWidgetMeta.addTab(tabFileInfo, "FileInfo")
        tabWidgetMeta.addTab(tabExif, "Exif")

        self.initFileInfoUI(tabFileInfo)
        self.initExifUI(tabExif)

        grouplayout.addWidget(tabWidgetMeta)
        groupbox.setLayout(grouplayout)

        imv = pg.ImageView()
        imv.ui.roiBtn.hide()
        imv.ui.menuBtn.hide()
        fileInfo = self.metadata.fileInfo.serialize()
        imv.setImage(self.image,
                     xvals=np.linspace(0., fileInfo['pixelPrecision'],
                                       self.image.shape[0]))

        hist = pg.HistogramLUTWidget(orientation='horizontal')
        hist.setImageItem(imv.getImageItem())

        groupboxHist = QGroupBox("Histogram", self.frame)
        grouplayoutHist = QVBoxLayout(groupboxHist)
        grouplayoutHist.addWidget(hist)

        framelayout.addWidget(groupbox)
        framelayout.addWidget(groupboxHist)
        self.frame.setLayout(framelayout)

    def initUI(self):
        self.initImageViewUI()
        self.initMetadataUI()

        hbox = QHBoxLayout()

        hbox.addWidget(self.tabWidget)
        hbox.addWidget(self.frame)
        hbox.setStretchFactor(self.tabWidget, 4)
        hbox.setStretchFactor(self.frame, 1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('Image Displayer')

    def convertNumpyArrayToQImage(self, img, metadata):
        if metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT8:
            image = np.array(img)
            if metadata.fileInfo.pixelType in [
                    PixelType.BAYER_RGGB, PixelType.BAYER_BGGR,
                    PixelType.BAYER_GRBG, PixelType.BAYER_GBRG
            ] or metadata.fileInfo.pixelType == PixelType.GRAYSCALE:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_Grayscale8)
            elif metadata.fileInfo.pixelType == PixelType.RGB:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGB888)
            elif metadata.fileInfo.pixelType == PixelType.RGBA:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGBA8888)
            else:
                QMessageBox.critical(
                    None, "Error",
                    "Unsupported pixel type  on 8 bits: {} ".format(
                        metadata.fileInfo.pixelType))

        elif metadata.fileInfo.pixelRepresentation == PixelRepresentation.UINT16:
            factor = 1
            if metadata.fileInfo.pixelPrecision:
                factor = int(65535.0 / (2 ** metadata.fileInfo.pixelPrecision - 1))
            image = np.array(img * factor)
            if metadata.fileInfo.pixelType in [
                    PixelType.BAYER_RGGB, PixelType.BAYER_BGGR,
                    PixelType.BAYER_GRBG, PixelType.BAYER_GBRG
            ] or metadata.fileInfo.pixelType == PixelType.GRAYSCALE:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_Grayscale16)
            elif metadata.fileInfo.pixelType == PixelType.RGBA:
                return QImage(image.data, image.shape[1], image.shape[0],
                              QImage.Format.Format_RGBA64)
            else:
                QMessageBox.critical(
                    None, "Error",
                    "Unsupported pixel type  on 16 bits: {} ".format(
                        metadata.fileInfo.pixelType))

        else:
            QMessageBox.critical(
                None, "Error", "Unsupported pixel representation: {} ".format(
                    metadata.fileInfo.pixelRepresentation))

    def showImage(self):
        qimage = self.convertNumpyArrayToQImage(self.image, self.metadata)
        px = QPixmap.fromImage(qimage)
        self.imagepic.resize(px.width(), px.height())
        self.imagepic.setPixmap(px)
        self.tabWidget.setCurrentIndex(0)

    def showMetadata(self):
        fileInfo = self.metadata.fileInfo.serialize()
        if 'fileFormat' in fileInfo:
            self.labfileFormatValue.setText(fileInfo['fileFormat'])
        if 'pixelRepresentation' in fileInfo:
            self.labpixelRepresentationValue.setText(
                fileInfo['pixelRepresentation'])
        if 'imageLayout' in fileInfo:
            self.labimageLayoutValue.setText(fileInfo['imageLayout'])
        if 'pixelType' in fileInfo:
            self.labpixelTypeValue.setText(fileInfo['pixelType'])
        if 'pixelPrecision' in fileInfo:
            self.labpixelPrecisionValue.setText(str(
                fileInfo['pixelPrecision']))
        if 'width' in fileInfo:
            self.labwidthValue.setText(str(fileInfo['width']))
        if 'height' in fileInfo:
            self.labheightValue.setText(str(fileInfo['height']))
        if 'widthAlignment' in fileInfo:
            self.labwidthAlignmentValue.setText(str(
                fileInfo['widthAlignment']))
        if 'heightAlignment' in fileInfo:
            self.labheightAlignmentValue.setText(
                str(fileInfo['heightAlignment']))
        if 'sizeAlignment' in fileInfo:
            self.labsizeAlignmentValue.setText(str(fileInfo['sizeAlignment']))

        exifMetadata = self.metadata.exifMetadata.serialize()
        if 'imageWidth' in exifMetadata:
            self.labimageWidthValue.setText(str(exifMetadata['imageWidth']))
        if 'imageHeight' in exifMetadata:
            self.labimageHeightValue.setText(str(exifMetadata['imageHeight']))
        if 'imageDescription' in exifMetadata:
            self.labimageDescriptionValue.setText(
                str(exifMetadata['imageDescription']))
        if 'make' in exifMetadata:
            self.labmakeValue.setText(str(exifMetadata['make']))
        if 'model' in exifMetadata:
            self.labmodelValue.setText(str(exifMetadata['model']))

        if 'orientation' in exifMetadata:
            self.laborientationValue.setText(str(exifMetadata['orientation']))
        if 'software' in exifMetadata:
            self.labsoftwareValue.setText(str(exifMetadata['software']))
        if 'exposureTime' in exifMetadata:
            self.labexposureTimeValue.setText(str(
                exifMetadata['exposureTime']))
        if 'fNumber' in exifMetadata:
            self.labfNumberValue.setText(str(exifMetadata['fNumber']))
        if 'isoSpeedRatings' in exifMetadata:
            self.labisoSpeedRatingsValue.setText(
                str(exifMetadata['isoSpeedRatings']))
        if 'dateTimeOriginal' in exifMetadata:
            self.labdateTimeOriginalValue.setText(
                str(exifMetadata['dateTimeOriginal']))
        if 'brightnessValue' in exifMetadata:
            self.labbrightnessValueValue.setText(
                str(exifMetadata['brightnessValue']))

        if 'exposureBiasValue' in exifMetadata:
            self.labexposureBiasValueValue.setText(
                str(exifMetadata['exposureBiasValue']))
        if 'focalLength' in exifMetadata:
            self.labfocalLengthValue.setText(str(exifMetadata['focalLength']))
        if 'focalLengthIn35mmFilm' in exifMetadata:
            self.labfocalLengthIn35mmFilmValue.setText(
                str(exifMetadata['focalLengthIn35mmFilm']))


def parse_command_line(argv):
    parser = argparse.ArgumentParser(
        description='Display image and metadata.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-i',
                               '--image',
                               required=True,
                               type=str,
                               help='Path to image file')

    parser.add_argument('-m',
                        '--metadata',
                        type=str,
                        default=None,
                        help='Path to image metadata sidecar file.')
    return parser.parse_args(argv)


def main():
    args = parse_command_line(sys.argv[1:])

    try:
        image_path = pathlib.Path(args.image)
        metadata_path = pathlib.Path(args.metadata) if args.metadata else None
        image, metadata = read_image(image_path, metadata_path)

        app = QApplication(sys.argv)
        img_displayer = ImageDisplayer(image, metadata, image_path)
        img_displayer.resize(400, 300)
        img_displayer.move(300, 300)
        img_displayer.show()
    except Exception as e:
        sys.exit("Exception caught in display image, check the error log: {}.".
                 format(str(e)))
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
